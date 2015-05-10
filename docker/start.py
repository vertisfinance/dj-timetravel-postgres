#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import signal
import sys


def main():
    sp = subprocess.Popen(['gosu', 'postgres', 'postgres'])

    def cleanup(signum, frame):
        sp.send_signal(signal.SIGINT)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    sys.exit(sp.wait())


if __name__ == '__main__':
    main()
