from time import sleep

from mdt.discoverer import Discoverer
from mdt.config import Config


class DevicesCommand:
    '''Usage: mdt devices

Returns a list of device names and IP addresses found on the local network
segment. Also indicates if a given device is marked as your default.

Variables used:
   preferred-device: contains the device name you want as your default

Note: MDT uses a python implementation of mDNS ZeroConf for discovery, so
it does not require a running Avahi daemon.
'''

    def __init__(self):
        self.discoverer = Discoverer()
        self.device = Config().preferredDevice()

    def run(self, args):
        sleep(1)
        print('Devices found:')
        discoveries = self.discoverer.discoveries
        for host, address in discoveries.items():
            if self.device and host == self.device:
                print('{0}\t\t({1},default)'.format(host, address))
            else:
                print('{0}\t\t({1})'.format(host, address))


class DevicesWaitCommand:
    '''Usage: mdt wait-for-device

Waits for either the first device found, or your preferred device to be
discovered on the local network segment.

Variables used:
   preferred-device: contains the device name you want as your default

Note: if preferred-device is cleared, then this will return on the first
available device found. Also, MDT uses a python implementation of mDNS
ZeroConf for discovery, so it does not require a running Avahi daemon.
'''

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
