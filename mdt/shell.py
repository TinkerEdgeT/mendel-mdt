from time import sleep

import platform
import subprocess
import os
import socket
import select
import sys
import termios
import tty

import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException

import discoverer
import config
import console
import keys

class KeyPushError(Exception):
    pass

class DefaultLoginError(Exception):
    pass

class SshClient:
    def __init__(self, device, address):
        self.config = config.Config()
        self.keystore = keys.Keystore()

        self.device = device
        self.address = address

        self.username = self.config.username()
        self.password = self.config.password()
        self.ssh_command = self.config.sshCommand()

        if not self.maybeGenerateSshKeys():
            return False

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    def _shouldPushKey(self):
        try:
            self.client.connect(
                self.address,
                username=self.username,
                pkey=self.keystore.key(),
                allow_agent=False,
                look_for_keys=False,
                compress=True)
        except AuthenticationException as e:
            return True
        except (SSHException, socket.error) as e:
            raise e
        finally:
            self.client.close()

    def _pushKey(self):
        try:
            self.client.connect(
                    self.address,
                    username=self.username,
                    password=self.password,
                    allow_agent=False,
                    look_for_keys=False,
                    compress=True)
        except AuthenticationException as e:
            raise DefaultLoginError(e)
        except (SSHException, socket.error) as e:
            raise KeyPushError(e)
        else:
            public_key = self.keystore.key().get_base64()
            self.client.exec_command('mkdir -p $HOME/.ssh')
            self.client.exec_command(
                'echo ssh-rsa {0} mdt@localhost >>$HOME/.ssh/authorized_keys'.format(public_key))
        finally:
            self.client.close()

    def maybeGenerateSshKeys(self):
        if not self.keystore.key():
            print('Looks like you don\'t have a private key yet. Generating one.')

            if not self.keystore.generateKey():
                print('Unable to generate private key.')
                return False

        return True

    def openShell(self):
        term = os.getenv("TERM", default="vt100")
        width, height = os.get_terminal_size()

        if self._shouldPushKey():
            print("Key not present on {0} -- pushing".format(self.device))
            self._pushKey()

        self.client.connect(
            self.address,
            username=self.username,
            pkey=self.keystore.key(),
            allow_agent=False,
            look_for_keys=False,
            compress=True)
        return self.client.invoke_shell(term=term, width=width, height=height)

    def close(self):
        self.client.close()


class Shell:
    def __init__(self):
        self.config = config.Config()
        self.discoverer = discoverer.Discoverer(self)
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

        if not self.address:
            if self.device:
                print('Waiting for device {0}...'.format(self.device))
            else:
                print('Waiting for a device...')

            while not self.address:
                sleep(0.1)

        print('Connecting to {0} at {1}'.format(self.device, self.address))

        try:
            client = SshClient(self.device, self.address)
            channel = client.openShell()
            cons = console.Console(channel, sys.stdin)
            cons.run()
        except KeyPushError as e:
            print("Unable to push keys to the device: {0}".format(e))
            return 1
        except DefaultLoginError as e:
            print("Can't login using default credentials: {0}".format(e))
            return 1
        except SSHException as e:
            print("Couldn't establish ssh connection to device: {0}".format(e))
            return 1
        except socket.error as e:
            print("Couldn't establish ssh connection to device: {0}".format(e))
            return 1
        except console.SocketTimeoutError as e:
            print("Connection to {0} at {1} closed: socket timeout".format(self.device, self.address))
            return 1
        except console.ConnectionClosedError as e:
            print("Connection to {0} at {1} closed".format(self.device, self.address))
            return 0
        finally:
            client.close()
