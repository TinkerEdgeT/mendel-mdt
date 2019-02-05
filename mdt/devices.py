from time import sleep

from discoverer import Discoverer

class DevicesCommand:
    def __init__(self):
        self.discoverer = Discoverer()

    def run(self, args):
        sleep(1)
        print('Devices found:')
        discoveries = self.discoverer.discoveries
        for host, address in discoveries.items():
            print('%s\t\t%s' % (host, address))

class DevicesWaitCommand:
    def __init__(self):
        self.discoverer = Discoverer()

    def run(self, args):
        print('Waiting for device...')
        found_device = False
        while True:
            sleep(1)
            discoveries = self.discoverer.discoveries
            if discoveries:
                break
        print('Devices found:')
        for host, address in self.discoverer.discoveries.items():
            print('%s\t\t%s' % (host, address))
