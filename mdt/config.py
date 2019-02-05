import sys
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "mdt")

class Config:
    def __init__(self):
        self.ensureConfigDirExists()

    def ensureConfigDirExists(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, mode=0o700)

    def getAttribute(self, name):
        path = os.path.join(CONFIG_DIR, name)
        if os.path.exists(path):
            with open(path, "r") as fp:
                return fp.readline().rstrip()
        return None

    def setAttribute(self, name, value):
        path = os.path.join(CONFIG_DIR, name)
        with open(path, "w") as fp:
            fp.write(value + "\n")

    def clearAttribute(self, name):
        path = os.path.join(CONFIG_DIR, name)
        if os.path.exists(path):
            os.unlink(path)

    def defaultDeviceName(self, devicename=None):
        if not devicename:
            return self.getAttribute("devicename")
        self.setAttribute("devicename", devicename)

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
