from typing import cast
from zeroconf import ServiceBrowser, Zeroconf

import socket

class Discoverer:
    def __init__(self, listener = None):
        self.zeroconf = Zeroconf()
        self.discoveries = {}
        self.listener = listener
        browser = ServiceBrowser(self.zeroconf, "_google_mdt._tcp.local.", self)

    def add_service(self, zeroconf, type, name):
        info = self.zeroconf.get_service_info(type, name)
        if info:
            hostname = info.server.split('.')[0]
            address = socket.inet_ntoa(cast(bytes, info.address))
            self.discoveries[hostname] = address
            if self.listener and hasattr(self.listener, "add_device"):
                self.listener.add_device(hostname, address)

    def remove_service(self, zeroconf, type, name):
        info = self.zeroconf.get_service_info(type, name)
        if self.listener and hasattr(self.listener, "remove_device"):
            self.listener.remove_device(info.server, self.discoveries[info.server])
        del(self.discoveries[info.server])
