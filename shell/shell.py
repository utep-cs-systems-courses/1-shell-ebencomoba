#! /usr/bin/env python3

import os, sys, re

# Changes directory
def change_dir(cmnds):
    try:
        os.chdir(cmnds[1])
    except FileNotFoundError:
        os.write(2, (f'\tNo such directory {cmnds[1]}\n').encode())

# Handles redirection
def redirect(cmnds, idx):
    # idx need to have parameters before and after
    if idx == 0 or idx == len(cmnds)-1:
        return
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
    del cmnds[idx+1]
    del cmnds[idx]
    execute_command(cmnds)

# Attempt to execute command, exit if it fails
def execute_command(cmnds):
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

def use_pipes(cmnds, idx):
    # Create pipe and sides for writing and reading
    toPipe, fromPipe = os.pipe()
    os.set_inheritable(toPipe, True)
    os.set_inheritable(fromPipe, True)
    left_cmnd = cmnds[0:idx]
    right_cmnd = cmnds[idx+1:]
    
    child = os.fork()
    if child < 0:
        os.write(2, ("\tFork failed, returning %d\n" % child).encode())
        sys.exit(3)
    # Writing to pipe
    elif child == 0:
        os.close(1)
        os.dup(fromPipe)
        os.set_inheritable(1, True)
        execute_command(left_cmnd)
    # Reading from pipe
    else:
        os.close(0)
        os.dup(toPipe)
        os.set_inheritable(0, True)
        os.wait()
        os.close(fromPipe)
        os.close(toPipe)
        execute_command(right_cmnd)

def main():
    # Program will run until exit command
    while (True):
    
        os.write(1, (f'{os.getcwd()} $ ').encode())
        cmnds = os.read(0, 100).decode().split()

        # No input, repeat
        if len(cmnds) == 0:
            break;
    
        # Exit command is executed
        if cmnds[0] == "exit":
            os.write(2, ("\tProgram terminated with exit command\n").encode())
            sys.exit(0)
    
        # Change directory is correctly typed and executed
        if cmnds[0] == "cd":
            if len(cmnds) == 2:
                change_dir(cmnds)
            else:
                os.write(2, ("\tcd accepts only one argument\n").encode())
            continue

        # Raise background task flag
        background = False
        if cmnds[len(cmnds)-1] == '&':
            background = True
            del cmnds[len(cmnds)-1]

        # We try to execute a command
        child = os.fork()
        # If forks fails, we exit
        if (child < 0):
            os.write(2, ("\tFork failed, returning %d\n" % child).encode())
            sys.exit(3)

        # Child tries to execute the command(s)
        elif (child == 0):
            # Looking for redirection
            if '>' in cmnds:
                redirect(cmnds, cmnds.index('>'))
            elif '<' in cmnds:
                redirect(cmnds, cmnds.index('<'))
            elif '|' in cmnds:
                use_pipes(cmnds, cmnds.index('|'))
                sys.exit(0)
            else:
                execute_command(cmnds)

        else:
            # If foreground, we wait for the child
            if not background:
                childPidCode = os.wait()[1] >> 8
                # Code 0 = No error, Code 3 = Error was detected before
                if (childPidCode == 0 or childPidCode == 3):
                    pass
                else:
                    os.write(2, (f'\tProgram terminated with exit code {childPidCode}\n').encode())

if __name__ == "__main__":
    main()
