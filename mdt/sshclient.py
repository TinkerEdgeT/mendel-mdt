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
import http.client

import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException
from paramiko.client import AutoAddPolicy

from mdt import config
from mdt import discoverer
from mdt import keys
from mdt import sshclient


KEYMASTER_PORT = 41337


class KeyPushError(Exception):
    pass


class DefaultLoginError(Exception):
    pass


class PasswordAuthDisableError(Exception):
    pass


class SshClient:
    def __init__(self, device, address):
        self.config = config.Config()
        self.keystore = keys.Keystore()

        self.device = device
        self.address = address

        self.username = self.config.username()
        self.password = self.config.password()

        if not self.maybeGenerateSshKeys():
            return False

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

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
        connection = http.client.HTTPConnection(self.address, KEYMASTER_PORT)
        try:
            public_key = self.keystore.key().get_base64()
            authorized_keys_line = 'ssh-rsa {0} mdt\n'.format(public_key)
            connection.request('PUT', '/', authorized_keys_line)
            response = connection.getresponse()
        except ConnectionError as e:
            raise KeyPushError(e)
        finally:
            connection.close()

        # Ensure the key we just pushed allows us to login
        try:
            self.client.connect(
                self.address,
                username=self.username,
                pkey=self.keystore.key(),
                allow_agent=False,
                look_for_keys=False,
                compress=True)

            if self.config.shouldDisablePasswordAuth() == "true":
                print("Key push successful: disabling password authentication")
                self.client.exec_command(
                    "sudo sed -e's/^#?PasswordAuthentication.*/PasswordAuthentication no/g' -i "
                    "/etc/ssh/sshd_config")
                self.client.exec_command('sudo systemctl restart ssh')
        except AuthenticationException as e:
            raise KeyPushError(e)
        except (SSHException, socket.error) as e:
            raise KeyPushError(e)
        finally:
            self.client.close()

    def maybeGenerateSshKeys(self):
        if not self.keystore.key():
            print('Looks like you don\'t have a private key yet. '
                  'Generating one.')

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

    def shellExec(self, cmd, allocPty=False):
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

        session = self.client.get_transport().open_session()
        if allocPty:
            term = os.getenv("TERM", default="vt100")
            width, height = os.get_terminal_size()
            session.get_pty(term=term, width=width, height=height)
        session.exec_command(cmd)
        return session

    def openSftp(self):
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

        session = self.client.open_sftp()
        return session

    def close(self):
        self.client.close()
