#!/usr/bin/env python

import sys

def increment(id_string):
    return "{:04d}".format(int(id_string[:4]) + 1)

if __name__ == '__main__':
    for line in sys.stdin:
        pass

    sys.stdout.write(increment(line))
