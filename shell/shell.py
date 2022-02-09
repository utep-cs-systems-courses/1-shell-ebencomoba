#! /usr/bin/env python3

import os, sys, re

# Program will run until exit command
while (True):
    cmnds = input(f'{os.getcwd()} $ ').split()

    # No input, repeat
    if len(cmnds) == 0:
        continue
    # Exit command is correctly typed and executed
    elif len(cmnds) == 1 and cmnds[0] == "exit":
        print("\tProgram terminated with exit command")
        sys.exit(0)
    # Change directory is correctly typed and executed
    elif cmnds[0] == "cd":
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
        if (child < 0):
            os.write(2, ("Fork failed, returning %d\n" % child).enconde())
            sys.exit(1)
        elif (child == 0):
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, cmnds[0])
                try:
                    os.execve(program, cmnds, os.environ)
                except FileNotFoundError:
                    pass
            os.write(2, ("Child could not execute %s\n" % cmnds[0]).encode())
            sys.exit(1)
        else:
            os.wait()
            os.write(1, ("Parent here\n").encode())
