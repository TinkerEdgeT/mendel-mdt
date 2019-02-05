from time import sleep

import platform
import subprocess
import os

import spur

import discoverer
import config
import keys

class Shell:
    def __init__(self):
        self.config = config.Config()
        self.keystore = keys.Keystore()
        self.discoverer = discoverer.Discoverer(self)

        self.username = self.config.username()
        self.private_key = self.keystore.privateKey()
        self.ssh_command = self.config.sshCommand()

        self.device = self.config.preferredDevice()
        self.address = None

    def add_device(self, hostname, address):
        if not self.device:
            self.device = hostname
            self.address = address
        elif self.device == hostname:
            self.address = address

    def run(self, args):
        if len(args) > 1:
            self.device = args[1]

        if not self.private_key:
            # Need to call genkey first.
            print('Looks like you don\'t have a private key yet. Generating one.')

            if not self.keystore.generateKey():
                print('Unable to generate private key.')
                return 1

        if not self.address:
            if self.device:
                print('Waiting for device "{0}"...'.format(self.device))
            else:
                print('Waiting for a device...')

            while not self.address:
                sleep(0.1)

            print('Found "{0}" at {1}'.format(self.device, self.address))

        os.execvp(
            self.ssh_command, [
                self.ssh_command,
                '-oStrictHostKeyChecking=no',
                '-i{0}'.format(self.keystore.privateKeyPath()),
                '-Ct',
                '@'.join([self.username, self.address])
            ])
