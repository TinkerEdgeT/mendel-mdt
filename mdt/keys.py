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
import platform
import shutil
import subprocess

import paramiko
from paramiko.ssh_exception import SSHException, PasswordRequiredException
from paramiko.rsakey import RSAKey

from mdt import config


SUPPORTED_SYSTEMS = [
    'Linux',
    'MacOS',
    'BSD',
]

KEYSDIR = os.path.join(config.CONFIG_BASEDIR, "keys")
KEYFILE_PATH = os.path.join(config.CONFIG_BASEDIR, "keys", "mdt.key")


class Keystore:
    def __init__(self):
        if not os.path.exists(config.CONFIG_BASEDIR):
            os.makedirs(CONFIG_BASEDIR, mode=0o700)
        if not os.path.exists(KEYSDIR):
            os.makedirs(KEYSDIR, mode=0o700)
        if not os.path.exists(KEYFILE_PATH):
            self.pkey = None
        else:
            try:
                self.pkey = RSAKey.from_private_key_file(KEYFILE_PATH)
            except IOError as e:
                print("Unable to read private key from file: {0}".format(e))
                sys.exit(1)
            except PasswordRequiredException as e:
                print("Unable to load in private key: {0}".format(e))
                sys.exit(1)

    def generateKey(self):
        self.pkey = RSAKey.generate(bits=4096)

        try:
            self.pkey.write_private_key_file(KEYFILE_PATH)
        except IOError as e:
            print("Unable to write private key to disk: {0}".format(e))
            return False
        else:
            return True

    def key(self):
        return self.pkey


class GenKeyCommand:
    '''Usage: mdt genkey

Generates an SSH key and stores it to disk.

Note that this does not prompt if you want to replace an already existing
key and will happily overwrite without telling you! Also note, you should remove
the keys previously stored on the device in $HOME/.ssh/authorized_keys and
restart the mdt-keymaster service on the device to re-push any newly generated
keys.
'''

    def run(self, args):
        if os.path.exists(KEYFILE_PATH):
            os.unlink(KEYFILE_PATH)
        keystore = Keystore()
        if not keystore.generateKey():
            return 1
        return 0


class SetKeyCommand:
    '''Usage: mdt setkey <path-to-private-key>

Copies an SSH private key provided into the MDT key store for use with
authentication later.'''

    def run(self, args):
        if len(args) != 2:
            print("Usage: mdt setkey <path-to-private-key>")
            return 1

        source_keyfile = args[1]
        if not os.path.exists(source_keyfile):
            print("Can't copy {0}: no such file or directory.".format(source_keyfile))
            return 1

        shutil.copy(source_keyfile, KEYFILE_PATH)
        print("Key {0} imported.".format(source_keyfile))
        return 0
