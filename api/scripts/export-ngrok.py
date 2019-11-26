#!/usr/bin/env python

import sys
import requests

if __name__ == '__main__':
    response = requests.get('http://localhost:4040/api/tunnels').json()

    for tunnel in response.get('tunnels', []):
        if tunnel['proto'] != 'https':
            continue

        if tunnel['config']['addr'] != 'http://localhost:6011':
            continue

        sys.stdout.write(tunnel['public_url'])
        break
