#!/usr/bin/env python3

import glob
import hwdata
import os
import platform
import re
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

class Platform:
    def __init__(self):
        self.hostname = socket.getfqdn()
        self.machine = platform.machine()
        self.release = platform.release()
        self.version = platform.version()

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

class HardDrive:
    def __init__(self):
        self.devices_list = []

    def get_devices(self):
        for dev_dirname in glob.glob('/sys/block/*'):
            dev = os.path.basename(dev_dirname)

            if not re.match(r'^dm|^loop|^zram|^sr', dev):
                self.devices_list.append(dev)

        return self.devices_list

    def get_device_info(self, dev_name):
        dev_properties = {}

        if os.path.exists('/sys/block/%s' %(dev_name)):
            dev_properties['device_name'] = dev_name
            dev_properties['device_model'] = read_sysfs_value('/sys/block/%s/device/model' %(dev_name))
            dev_properties['device_firmware_version'] = read_sysfs_value('/sys/block/%s/device/firmware_rev' %(dev_name))
            dev_properties['device_size'] = read_sysfs_value('/sys/block/%s/size' %(dev_name))
        else:
            pass

        return dev_properties

class NetworkDevice:
    def __init__(self):
        self.interfaces_list = []

    def get_interfaces(self):
        for dev_dirname in glob.glob('/sys/class/net/*'):
            dev = os.path.basename(dev_dirname)

            if not re.match(r'^virbr|^lo', dev):
                self.interfaces_list.append(dev)

        return self.interfaces_list

    def get_interface_info(self, dev_name):
        interface_properties = {}

        if os.path.exists('/sys/class/net/%s' %(dev_name)):
            pci = hwdata.PCI()

            interface_vendor_id = read_sysfs_value('/sys/class/net/%s/device/vendor' %(dev_name))[2:]
            interface_device_id = read_sysfs_value('/sys/class/net/%s/device/device' %(dev_name))[2:]

            interface_vendor_name = pci.get_vendor(interface_vendor_id)
            interface_device_name = pci.get_device(interface_vendor_id, interface_device_id)

            interface_properties['interface_name'] = dev_name
            interface_properties['interface_vendor_name'] = interface_vendor_name
            interface_properties['interface_device_name'] = interface_device_name
        else:
            pass

        return interface_properties

