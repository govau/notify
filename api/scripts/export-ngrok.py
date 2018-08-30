#!/usr/bin/env python

import os
import sys
import requests

if __name__ == '__main__':
    response = requests.get('http://localhost:4040/api/tunnels').json()

    for tunnel in response.get('tunnels', []):
        if tunnel['proto'] != 'https':
            pass

        if tunnel['config']['addr'] != 'localhost:6011':
            pass

        sys.stdout.write(tunnel['public_url'])
