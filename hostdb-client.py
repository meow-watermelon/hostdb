#!/usr/bin/env python3

import os
import platform
import socket

class BIOS:
    def __init__(self):
        self.bios_date = None
        self.bios_release = None
        self.bios_vendor = None
        self.bios_version = None

    def get_bios_info(self):
        try:
            with open('/sys/devices/virtual/dmi/id/bios_date', 'rt') as f:
                data = f.readlines()
                self.bios_date = data[0].strip()
        except:
            pass

        try:
            with open('/sys/devices/virtual/dmi/id/bios_release', 'rt') as f:
                data = f.readlines()
                self.bios_release = data[0].strip()
        except:
            pass

        try:
            with open('/sys/devices/virtual/dmi/id/bios_vendor', 'rt') as f:
                data = f.readlines()
                self.bios_vendor = data[0].strip()
        except:
            pass

        try:
            with open('/sys/devices/virtual/dmi/id/bios_version', 'rt') as f:
                data = f.readlines()
                self.bios_version = data[0].strip()
        except:
            pass

class Platform:
    def __init__(self):
        self.hostname = socket.getfqdn()
        self.machine = platform.machine()
        self.release = platform.release()
        self.version = platform.version()

