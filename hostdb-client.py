#!/usr/bin/env python3

import os
import platform
import socket

# a function to read one-line sysfs file and return its value
def read_sysfs_value(sysfs_filename):
    sysfs_value = None

    try:
        with open(sysfs_filename, 'rt') as f:
            sysfs_value = f.readlines()[0].strip()
    except:
        pass

    return sysfs_value

class BIOS:
    def __init__(self):
        self.bios_date = read_sysfs_value('/sys/devices/virtual/dmi/id/bios_date')
        self.bios_release = read_sysfs_value('/sys/devices/virtual/dmi/id/bios_release')
        self.bios_vendor = read_sysfs_value('/sys/devices/virtual/dmi/id/bios_vendor')
        self.bios_version = read_sysfs_value('/sys/devices/virtual/dmi/id/bios_version')

class Board:
    def __init__(self):
        self.board_name = read_sysfs_value('/sys/devices/virtual/dmi/id/board_name')
        self.board_serial = read_sysfs_value('/sys/devices/virtual/dmi/id/board_serial')
        self.board_vendor = read_sysfs_value('/sys/devices/virtual/dmi/id/board_vendor')

class Chassis:
    def __init__(self):
        self.chassis_serial = read_sysfs_value('/sys/devices/virtual/dmi/id/chassis_serial')
        self.chassis_vendor = read_sysfs_value('/sys/devices/virtual/dmi/id/chassis_vendor')

class Product:
    def __init__(self):
        self.product_family = read_sysfs_value('/sys/devices/virtual/dmi/id/product_family')
        self.product_name = read_sysfs_value('/sys/devices/virtual/dmi/id/product_name')
        self.product_serial = read_sysfs_value('/sys/devices/virtual/dmi/id/product_serial')
        self.product_sku = read_sysfs_value('/sys/devices/virtual/dmi/id/product_sku')

class Platform:
    def __init__(self):
        self.hostname = socket.getfqdn()
        self.machine = platform.machine()
        self.release = platform.release()
        self.version = platform.version()

