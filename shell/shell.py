#! /usr/bin/env python3

import os, sys, re

# Changes directory
def change_dir(cmnds):
    try:
        os.chdir(cmnds[1])
    except FileNotFoundError:
        print(f'\tNo such directory {cmnds[1]}')

# Handles redirection
def redirect(cmnds, idx):
    # Open file (or create it) to write result of command
    if cmnds[idx] == '>':
        os.close(1)
        os.open(cmnds[idx+1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1, True)
    # Open file to read contents
    else:
        os.close(0)
        os.open(cmnds[idx+1], os.O_RDONLY)
        os.set_inheritable(0, True)

# Program will run until exit command
while (True):
    cmnds = input(f'{os.getcwd()} $ ').split()

    # No input, repeat
    if len(cmnds) == 0:
        continue
    
    # Exit command is executed
    if cmnds[0] == "exit":
        print("\tProgram terminated with exit command")
        sys.exit(0)
    
    # Change directory is correctly typed and executed
    if cmnds[0] == "cd":
        if len(cmnds) == 2:
            change_dir(cmnds)
        else:
            print("\tcd accepts only one argument")
        continue

    # Raise flag if background task
    background = False
    if cmnds[len(cmnds)-1] == '&':
        background = True
        del cmnds[len(cmnds)-1]

    # We try to execute a command
    child = os.fork()
    # If forks fails, we exit
    if (child < 0):
        os.write(2, ("\tFork failed, returning %d\n" % child).encode())
        sys.exit(1)

    # Child tries to execute the command(s)
    elif (child == 0):
        # Looking for redirection
        for idx in range(len(cmnds)):
            if (cmnds[idx] == '>' or cmnds[idx] == '<') and idx+2 <= len(cmnds):
                redirect(cmnds, idx)
                del cmnds[idx+1]
                del cmnds[idx]
                break
                
        # Try each directory in path
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, cmnds[0])
            try:
                os.execve(program, cmnds, os.environ)
            # Pass quietly to next attempt
            except FileNotFoundError:
                pass

        # If target file or directory was not found, we exit
        os.write(2, (f'\t{cmnds[0]}: command not found\n').encode())
        sys.exit(3)

    else:
        # If foreground, we wait for the child
        if not background:
            childPidCode = os.wait()[1] >> 8
            # Code 0 = No error, Code 3 = Error was detected before
            if (childPidCode == 0 or childPidCode == 3):
                pass
            else:
                os.write(2, (f'\tProgram terminated with exit code {childPidCode}\n').encode())
