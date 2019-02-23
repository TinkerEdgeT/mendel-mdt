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
import time

from mdt import command
from mdt import config
from mdt import console
from mdt import discoverer
from mdt import sshclient


PROGRESS_WIDTH = 45
FILENAME_WIDTH = 30


def MakeProgressFunc(full_filename, width, char='>'):
    def closure(bytes_xferred, total_bytes):
        filename = full_filename
        if len(filename) > FILENAME_WIDTH:
            filename = filename[0:FILENAME_WIDTH - 3] + '...'

        pcnt = bytes_xferred / total_bytes
        left = char * round(pcnt * width)
        right = ' ' * round((1 - pcnt) * width)
        pcnt = '%3d' % (int(pcnt * 100))
        sys.stdout.write('\r{0}% |{1}{2}| {3}'.format(
            pcnt, left, right, filename))
        sys.stdout.flush()

    return closure


class InstallCommand(command.NetworkCommand):
    def preConnectRun(self, args):
        if len(args) < 2:
            print("Usage: mdt install [<package-filename...>]")
            return False

        return True

    def runWithClient(self, client, args):
        package_to_install = args[1]
        package_filename = os.path.basename(package_to_install)
        remote_filename = os.path.join('/tmp', package_filename)

        sftp_callback = MakeProgressFunc(package_filename, PROGRESS_WIDTH)
        sftp = client.openSftp()
        sftp.put(package_to_install, remote_filename, callback=sftp_callback)
        sftp.close()
        client.close()
        print()

        channel = client.shellExec("sudo /usr/sbin/mdt-install-package {0}; "
                                   "rm -f {0}".format(remote_filename),
                                   allocPty=True)
        cons = console.Console(channel, sys.stdin)
        return cons.run()


class PushCommand(command.NetworkCommand):
    def preConnectRun(self, args):
        if len(args) < 3:
            print("Usage: mdt push <filename...> <destination-directory>")
            return False

        for file in args[1:-1]:
            if not os.path.isfile(file):
                print("{0}: Is a directory -- cannot push".format(file))
                return False

        return True

    def runWithClient(self, client, args):
        files_to_push = args[1:-1]
        destination = args[-1]

        try:
            sftp = client.openSftp()
            for file in files_to_push:
                base_filename = os.path.basename(file)
                sftp_callback = MakeProgressFunc(file, PROGRESS_WIDTH)
                remote_filename = os.path.join(destination, base_filename)

                sftp_callback(0, 1)
                sftp.put(file, remote_filename, callback=sftp_callback)
                sftp_callback(1, 1)
                print()
        finally:
            print()
            sftp.close()

        return 0


class PullCommand(command.NetworkCommand):
    def preConnectRun(self, args):
        if len(args) < 3:
            print("Usage: mdt pull [<filename...>]")
            return False

        return True

    def runWithClient(self, client, args):
        files_to_pull = args[1:-1]
        destination = args[-1]

        try:
            sftp = client.openSftp()
            for file in files_to_pull:
                base_filename = os.path.basename(file)
                sftp_callback = MakeProgressFunc(file,
                                                 PROGRESS_WIDTH,
                                                 char='<')
                destination_filename = os.path.join(destination, base_filename)

                sftp_callback(0, 1)
                sftp.get(file, destination_filename, callback=sftp_callback)
                sftp_callback(1, 1)
                print()
        finally:
            print()
            sftp.close()

        return 0
