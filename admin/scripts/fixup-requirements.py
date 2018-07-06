#!/usr/bin/env python

import os
import sys


def get_eggname(directory):
    return {'utils': 'notifications-utils'}.get(directory)


if __name__ == '__main__':
    for line in sys.stdin:
        if not line.startswith('-e'):
            sys.stdout.write(line)
            continue

        path = line[2:].strip()
        directory = os.path.basename(os.path.normpath(path))
        egg = get_eggname(directory)
        if egg:
            sys.stdout.write('%s\n' % egg)
