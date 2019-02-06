import os
import platform
import subprocess

import paramiko
from paramiko.ssh_exception import SSHException, PasswordRequiredException

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
                self.pkey = paramiko.rsakey.RSAKey.from_private_key_file(KEYFILE_PATH)
            except IOError as e:
                print("Unable to read private key from file: {0}".format(e))
                sys.exit(1)
            except PasswordRequiredException as e:
                print("Unable to load in private key: {0}".format(e))
                sys.exit(1)

    def generateKey(self):
        self.pkey = paramiko.rsakey.RSAKey.generate(bits=4096)

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
key and will happily overwrite without telling you!
'''

    def run(self, args):
        if os.path.exists(KEYFILE_PATH):
            os.unlink(KEYFILE_PATH)
        keystore = Keystore()
        if not keystore.generateKey():
            return 1
        return 0
