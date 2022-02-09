#! /usr/bin/env python3

import os, sys, re

# Program will run until exit command
while (True):
    cmnds = input(f'{os.getcwd()} $ ').split()

    # No input, repeat
    if len(cmnds) == 0:
        continue
    # Exit command is correctly typed and executed
    elif cmnds[0] == "exit":
        print("\tProgram terminated with exit command")
        sys.exit(0)
    # Change directory is correctly typed and executed
    elif cmnds[0] == "cd":
        # TODO - Function out of this part
        if len(cmnds) == 2:
            try:
                os.chdir(cmnds[1])
            except FileNotFoundError:
                print(f'\tNo such directory {cmnds[1]}')
            continue
        print("\tcd accepts only one directory")
    # We try to execute a command
    else:
        child = os.fork()
        # If forks fails, we exit
        if (child < 0):
            os.write(2, ("\tFork failed, returning %d\n" % child).encode())
            sys.exit(1)
        # Child tries to execute the command(s)
        elif (child == 0):
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
            childPidCode = os.wait()[1] >> 8
            if (childPidCode == 0 or childPidCode == 3):
                pass
            else:
                os.write(2, (f'\tProgram terminated with exit code {childPidCode}\n').encode())
