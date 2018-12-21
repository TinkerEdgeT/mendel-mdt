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
