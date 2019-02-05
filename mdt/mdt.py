#!/usr/bin/env python3

"""MDT - The Mendel Development Tool

This is the main CLI dispatch routine that teases out the command line and runs
the appropriate command.
"""

import socket
import sys

import config
import devices
import keys

class HelpCommand:
    def run(self, args):
        print('implement me')


COMMANDS = {
    'help': HelpCommand(),
    'devices': devices.DevicesCommand(),
    'wait-for-device': devices.DevicesWaitCommand(),
    'get': config.Get(),
    'set': config.Set(),
    'clear': config.Clear()
}


def main():
    if len(sys.argv) <= 1:
        command = 'help'
    else:
        command = sys.argv[1].lower()

    command = COMMANDS.get(command)
    if command != None:
        exit(command.run(sys.argv[1:]))


if __name__ == '__main__':
    main()
