import platform
import subprocess
import os

import config

SUPPORTED_SYSTEMS = [
    'Linux',
    'MacOS',
    'BSD',
]


class Keystore:
    def __init__(self):
        self.config = config.Config()
        self.private_key = self.config.getKey("mdt")
        self.public_key = self.config.getKey("mdt.pub")

    def generateKey(self):
        if platform.system() not in SUPPORTED_SYSTEMS:
            print('Sorry, MDT doesn\'t support generating SSH keys on platforms other than:')
            print('\n'.join(SUPPORTED_SYSTEMS))
            return False

        try:
            subprocess.run([
                "ssh-keygen",
                "-f",
                os.path.join(config.CONFIG_KEYSDIR, "mdt"),
                "-P",
                ""
            ], check=True)
        except FileNotFoundError as e:
            print('Couldn\'t find ssh-keygen in your PATH.')
            return False
        except subprocess.CalledProcessError as e:
            print('Couldn\'t generate SSH keys.')
            print('ssh-keygen failed with error code {0}'.format(e.returncode))
            return False

        return True

    def publicKey(self):
        return self.public_key

    def privateKey(self):
        return self.private_key

    def pushKey(self):
        pass


class GenKey:
    def __init__(self):
        self.keystore = Keystore()

    def run(self, args):
        self.keystore.generateKey()
