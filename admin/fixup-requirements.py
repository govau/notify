import urllib.parse
import sys

if __name__ == '__main__':
    for line in sys.stdin:
        if not line.startswith('-e'):
            sys.stdout.write(line)
            continue

        if '--ignore' in sys.argv:
            continue

        line = line[2:].strip()
        parsed = urllib.parse.urlparse(line)
        egg = next(iter(urllib.parse.parse_qs(parsed.fragment).get('egg')), None)

        if egg:
            sys.stdout.write('%s\n' % egg)
