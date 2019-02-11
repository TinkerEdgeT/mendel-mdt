#!/usr/bin/env python3

"""MDT - The Mendel Development Tool

This is the main CLI dispatch routine that teases out the command line and runs
the appropriate command.
"""

import socket
import sys

try:
    import paramiko
    import zeroconf
except:
    sys.stderr.write("Couldn't load paramiko or zeroconf -- perhaps you need to install them?\r\n")
    sys.stderr.write("On Debian derivatives, 'apt-get install python3-paramiko python3-zeroconf'.\r\n")
    sys.exit(1)

from mdt import config
from mdt import devices
from mdt import files
from mdt import keys
from mdt import shell


class HelpCommand:
    '''Usage: mdt help [<subcommand>]

Gets additional information about a given subcommand, or returns a summary
of subcommands available.
'''

    def run(self, args):
        if len(args) <= 1:
            print('Usage: mdt <subcommand> [<options>]')
            print()
            print('Where <subcommand> may be one of the following:')
            print('    help            - this command, gets help on another command.')
            print('    devices         - lists all detected devices.')
            print('    wait-for-device - waits for a device to be discovered on the network')
            print('    get             - gets an MDT variable value')
            print('    set             - sets an MDT variable value')
            print('    clear           - clears an MDT variable')
            print('    genkey          - generates an SSH key for connecting to a device')
            print('    shell           - opens an interactive shell to a device')
            print('    exec            - runs a shell command and returns the output and the exit code')
            print('    install         - installs a Debian package using mdt-install-package on the device')
            print('    push            - pushes a file (or files) to the device')
            print('    pull            - pulls a file (or files) from the device')
            print()
            print('Use "mdt help <subcommand>" for more details.')
            print()
            return 1

        subcommand = args[1].lower()
        command = COMMANDS[subcommand]
        if command.__doc__:
            print(command.__doc__)
        else:
            print("No help is available for subcommand '{0}' "
                  "-- please yell at the developers. :)".format(subcommand))


COMMANDS = {
    'clear': config.ClearCommand(),
    'devices': devices.DevicesCommand(),
    'exec': shell.ExecCommand(),
    'genkey': keys.GenKeyCommand(),
    'get': config.GetCommand(),
    'help': HelpCommand(),
    'install': files.InstallCommand(),
    'pull': files.PullCommand(),
    'push': files.PushCommand(),
    'reboot': shell.RebootCommand(),
    'reboot-bootloader': shell.RebootBootloaderCommand(),
    'set': config.SetCommand(),
    'shell': shell.ShellCommand(),
    'wait-for-device': devices.DevicesWaitCommand(),
}


def main():
    try:
        if len(sys.argv) <= 1:
            exit(COMMANDS['help'].run([]))
        else:
            command = sys.argv[1].lower()

        if command == '--help':
            command = 'help'

        if command in COMMANDS:
            command = COMMANDS[command]
            exit(command.run(sys.argv[1:]))

        print("Unknown command '{0}': try 'mdt help'".format(command))
        return 1

    except KeyboardInterrupt:
        print()
        exit(1)


if __name__ == '__main__':
    main()
