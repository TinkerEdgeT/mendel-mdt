'''
Copyright 2019 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


import os
import sys

from mdt import command
from mdt import console


class ShellCommand(command.NetworkCommand):
    '''Usage: mdt shell

Opens an interactive shell to either your preferred device or to the first
device found.

Variables used:
    preferred-device    - set this to your preferred device name to connect
                          to by default if no <devicename> is provided on the
                          command line. Can be set to an IPv4 address to bypass
                          the mDNS lookup.
    username            - set this to the username that should be used to
                          connect to a device with. Defaults to 'mendel'.
    password            - set this to the password to use to login to a new
                          device with. Defaults to 'mendel'. Only used
                          during the initial setup phase of pushing an SSH
                          key to the board.

If no SSH key is available on disk (ie: you didn't run genkey before running
shell), this will implicitly run genkey for you. Additionally, shell will
attempt to connect to a device by doing the following:

  1. Attempt a connection using your SSH key only, with no password.
  2. If the connection attempt failed due to authentication, will
     attempt to push the key to the device by using the default
     login credentials in the 'username' and 'password' variables.
  3. Installs your SSH key to the device after logging in.
  4. Disconnects and reconnects using the SSH key.
'''

    def runWithClient(self, client, args):
        channel = client.openShell()
        cons = console.Console(channel, sys.stdin)
        return cons.run()


class ExecCommand(command.NetworkCommand):
    '''Usage: mdt exec [<shell-command...>]

Opens a non-interactive shell to either your preferred device or to the first
device found.

Variables used:
    preferred-device    - set this to your preferred device name to connect
                          to by default if no <devicename> is provided on the
                          command line. Can be set to an IPv4 address to bypass
                          the mDNS lookup.
    username            - set this to the username that should be used to
                          connect to a device with. Defaults to 'mendel'.
    password            - set this to the password to use to login to a new
                          device with. Defaults to 'mendel'. Only used
                          during the initial setup phase of pushing an SSH
                          key to the board.

If no SSH key is available on disk (ie: you didn't run genkey before running
shell), this will implicitly run genkey for you. Additionally, shell will
attempt to connect to a device by doing the following:

  1. Attempt a connection using your SSH key only, with no password.
  2. If the connection attempt failed due to authentication, will
     attempt to push the key to the device by using the default
     login credentials in the 'username' and 'password' variables.
  3. Installs your SSH key to the device after logging in.
  4. Disconnects and reconnects using the SSH key.
'''
    def runWithClient(self, client, args):
        channel = client.shellExec(' '.join(args[1:]))
        cons = console.Console(channel, sys.stdin)
        return cons.run()


class RebootCommand(command.NetworkCommand):
    def runWithClient(self, client, args):
        channel = client.shellExec("sudo reboot")
        cons = console.Console(channel, sys.stdin)
        return cons.run()


class RebootBootloaderCommand(command.NetworkCommand):
    def runWithClient(self, client, args):
        channel = client.shellExec("sudo reboot-bootloader")
        cons = console.Console(channel, sys.stdin)
        return cons.run()


class PushKeyCommand(command.NetworkCommand):
    '''Usage: mdt pushkey [<path-to-ssh-public-key>]

Copies an SSH public key provided to the device's ~/.ssh/authorized_keys
file. If no public key is provided, attempts to push MDTs previously generated
public key from ~/.config/mdt/keys/mdt.key.
'''

    def runWithClient(self, client, args):
        key_to_push = None

        if len(args) == 1:
            # The key was most likely pushed by the NetworkCommand substrate. We
            # can simply return here.
            print("MDT Key pushed.")
            return 0

        if len(args) != 2:
            print("Usage: mdt pushkey [<path-to-public-key>]")
            return 1

        source_keyfile = args[1]
        if not os.path.exists(source_keyfile):
            print("Can't copy {0}: no such file or directory.".format(source_keyfile))
            return 1

        source_key = ''
        with open(args[1], 'rb') as fp:
            source_key = fp.read()

        sftp = client.openSftp()
        try:
            sftp.chdir('/home/mendel/.ssh')
        except FileNotFoundError as e:
            sftp.mkdir('/home/mendel/.ssh', mode=0o700)

        with sftp.open('/home/mendel/.ssh/authorized_keys', 'a+b') as fp:
            fp.write('\r\n')
            fp.write(source_key)

        print("Key {0} pushed.".format(source_keyfile))
        return 0
