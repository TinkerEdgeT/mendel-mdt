from time import sleep

from discoverer import Discoverer
from config import Config

class DevicesCommand:
    def __init__(self):
        self.discoverer = Discoverer()
        self.devicename = Config().defaultDeviceName()

    def run(self, args):
        sleep(1)
        print('Devices found:')
        discoveries = self.discoverer.discoveries
        for host, address in discoveries.items():
            if self.devicename and host == self.devicename:
                print('{0}\t\t({1},default)'.format(host, address))
            else:
                print('{0}\t\t({1})'.format(host, address))

class DevicesWaitCommand:
    def __init__(self):
        self.found_devices = False
        self.discoverer = Discoverer(self)

    def add_device(self, hostname, address):
        self.found_devices = True
        self.hostname = hostname
        self.address = address

    def run(self, args):
        print('Waiting for device...')
        while not self.found_devices:
            sleep(0.1)
        print('Device found: {0} ({1})'.format(self.hostname, self.address))
