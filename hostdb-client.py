#!/usr/bin/env python3

import collections
import glob
import hwdata
import os
import platform
import re
import socket
import subprocess

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

class CPU:
    def __init__(self):
        self.cpu_id_list = set()
        self.num_cpus = 0

    def get_cpu_info(self):
        cpu_properties_list = []
        # vendor id, model name, cpu id
        cpu_properties_draft = [[], [], []]

        try:
            with open('/proc/cpuinfo', 'rt') as f:
                for line in f.readlines():
                    # process vendor id
                    vendor_id_match = re.match(r'^vendor_id\s+:\s+(.*)', line.strip())

                    if vendor_id_match and vendor_id_match.groups():
                        cpu_properties_draft[0].append(vendor_id_match.groups()[0])

                    # process model name
                    model_name_match = re.match(r'^model name\s+:\s+(.*)', line.strip())

                    if model_name_match and model_name_match.groups():
                        cpu_properties_draft[1].append(model_name_match.groups()[0])

                    # process cpu id
                    cpu_id_match = re.match(r'^physical id\s+:\s+(\d+)', line.strip())

                    if cpu_id_match and cpu_id_match.groups():
                        cpu_properties_draft[2].append(cpu_id_match.groups()[0])
        except:
            return None
        else:
            # set up attributes
            self.cpu_id_list = set(cpu_properties_draft[2])
            self.num_cpus = len(self.cpu_id_list)

            # generate cpu(s) list
            for cpu_id in self.cpu_id_list:
                cpu_id_index = cpu_properties_draft[2].index(cpu_id)
                cpu_vendor_id = cpu_properties_draft[0][cpu_id_index]
                cpu_model_name = cpu_properties_draft[1][cpu_id_index]

                cpu_string = cpu_vendor_id + ' ' + cpu_model_name
                cpu_properties_list.append(cpu_string)

            return collections.Counter(cpu_properties_list)

class Memory:
    def __init__(self):
        # total size unit: kB
        self.total_size = 0

    def get_memory_total_size(self):
        try:
            with open('/proc/meminfo', 'rt') as f:
                while True:
                    memory_match = re.match('^MemTotal:\s+(\d+)\s+kB', f.readline().strip())

                    if memory_match and memory_match.groups():
                        self.total_size = memory_match.groups()[0]
                        break
        except:
            pass
        else:
            return self.total_size

    def get_memory_info(self):
        try:
            dmidecode_run = subprocess.run(['dmidecode', '-t', 'memory'], capture_output=True)
        except:
            return None
        else:
            if dmidecode_run.returncode == 0:
                memory_size = []

                dmidecode_memory_output = dmidecode_run.stdout.decode().split('\n')

                for entry in dmidecode_memory_output:
                    size_match = re.match('^\s+Size:\s+(\d+\s+\w+)', entry)

                    if size_match and size_match.groups():
                        memory_size.append(size_match.groups()[0])

                return collections.Counter(memory_size)
            else:
                return None

