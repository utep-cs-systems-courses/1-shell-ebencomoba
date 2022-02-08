#! /usr/bin/env python3

import os, sys, re

while (True):
    cmnds = input(f'{os.getcwd()} $ ').split()

    if len(cmnds) == 0:
        continue
    elif len(cmnds) == 1 and cmnds[0] == "exit":
        print("\tProgram terminated with exit command")
        sys.exit(0)
    elif cmnds[0] == "cd":
        if len(cmnds) == 2:
            try:
                os.chdir(cmnds[1])
            except FileNotFoundError:
                print(f'\tNo such directory {cmnds[1]}')
            continue
        print("\tcd accepts only one directory")
    else:
        child = os.fork()
        if (child < 0):
            os.write(2, ("Fork failed, returning %d\n" % child).enconde())
            sys.exit(1)
        elif (child == 0):
            os.write(1, ("Child here\n").encode())
            sys.exit(0)
        else:
            os.wait()
            os.write(1, ("Parent here\n").encode())
