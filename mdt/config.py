import os
import sys


CONFIG_BASEDIR = os.path.join(os.path.expanduser("~"), ".config", "mdt")
CONFIG_ATTRDIR = os.path.join(CONFIG_BASEDIR, "attribs")

DEFAULT_USERNAME = "mendel"
DEFAULT_PASSWORD = "mendel"
DEFAULT_SSH_COMMAND = "ssh"


class Config:
    def __init__(self):
        self.ensureConfigDirExists()

    def ensureConfigDirExists(self):
        if not os.path.exists(CONFIG_BASEDIR):
            os.makedirs(CONFIG_BASEDIR, mode=0o700)
        if not os.path.exists(CONFIG_ATTRDIR):
            os.makedirs(CONFIG_ATTRDIR, mode=0o700)

    def getAttribute(self, name, default=None):
        path = os.path.join(CONFIG_ATTRDIR, name)
        if os.path.exists(path):
            with open(path, "r") as fp:
                return fp.readline().rstrip()

        return default

    def setAttribute(self, name, value):
        path = os.path.join(CONFIG_ATTRDIR, name)
        with open(path, "w") as fp:
            fp.write(value + "\n")

    def clearAttribute(self, name):
        path = os.path.join(CONFIG_ATTRDIR, name)
        if os.path.exists(path):
            os.unlink(path)

    def preferredDevice(self, devicename=None):
        if not devicename:
            return self.getAttribute("preferred-device")
        self.setAttribute("preferred-device", devicename)

    def username(self, username=None):
        if not username:
            return self.getAttribute("username", DEFAULT_USERNAME)
        self.setAttribute("username", username)

    def password(self, password=None):
        if not password:
            return self.getAttribute("password", DEFAULT_PASSWORD)
        self.setAttribute("password", password)

    def sshCommand(self, command=None):
        if not command:
            return self.getAttribute("ssh-command", DEFAULT_SSH_COMMAND)
        self.setAttribute("ssh-command", command)


class Get:
    def __init__(self):
        self.config = Config()

    def run(self, args):
        if args:
            print("{0}: {1}".format(args[1], self.config.getAttribute(args[1])))


class Set:
    def __init__(self):
        self.config = Config()

    def run(self, args):
        if args:
            self.config.setAttribute(args[1], args[2])
            print("Set {0} to {1}".format(args[1], args[2]))


class Clear:
    def __init__(self):
        self.config = Config()

    def run(self, args):
        if args:
            self.config.clearAttribute(args[1])
            print("Cleared {0}".format(args[1]))
