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


from typing import cast
from zeroconf import ServiceBrowser, Zeroconf

import socket


class Discoverer:
    def __init__(self, listener=None):
        self.zeroconf = Zeroconf()
        self.discoveries = {}
        self.listener = listener
        self.browser = ServiceBrowser(self.zeroconf, "_googlemdt._tcp.local.", self)

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
            self.listener.remove_device(info.server,
                                        self.discoveries[info.server])
        if info.server in self.discoveries:
            del(self.discoveries[info.server])

    def stop(self):
        self.browser.cancel()
