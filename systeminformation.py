import json
import uuid
from winreg import HKEYType
import subprocess
import wmi
import winreg
import socket
import requests


class SystemInformation:
    def __init__(self, reg_conn: HKEYType):
        self.__reg_conn = reg_conn
        self.__w = wmi.WMI()
        self.__mac = self._mac()
        self.__cpuid = self._cpuid()
        self.__motherboard = self._motherboard()
        self.__bios = self._bios()
        self.__disk_serial = self._disk_serial()
        self.__machineguid = self._machine_guid()
        self.__uuid = self._uuid()
        self.__local_ip = self._local_ip()
        self.__public_ip = self._public_ip()

    def print(self):
        print("MAC: " + (self.mac or "Invalid MAC"))
        print("CPUID: " + (self.cpuid or "Invalid CPUID"))
        print("Motherboard: " + (self.motherboard or "Invalid Motherboard number"))
        print("BIOS: " + (self.bios or "Invalid BIOS number"))
        print("DISK Serial: " + (self.disk_serial or "Invalid Serial"))
        print("Machine GUID: " + (self.machine_guid or "Invalid Machine GUID"))
        print("UUID: " + (self.uuid or "Invalid UUID"))
        print("Local IP: " + (self.local_ip or "Invalid Local IP"))
        print("Public IP: " + (self.public_ip or "Invalid Public IP"))

    @property
    def mac(self):
        return self.__mac

    @property
    def cpuid(self):
        return self.__cpuid

    @property
    def motherboard(self):
        return self.__motherboard

    @property
    def bios(self):
        return self.__bios

    @property
    def disk_serial(self):
        return self.__disk_serial

    @property
    def machine_guid(self):
        return self.__machineguid

    @property
    def uuid(self):
        return self.__uuid

    @property
    def local_ip(self):
        return self.__local_ip

    @property
    def public_ip(self):
        return self.__public_ip

    def _mac(self):
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
        return mac

    def _cpuid(self):
        for cpu in self.__w.Win32_Processor():
            if cpu.ProcessorId:
                return cpu.ProcessorId
        return None

    def _motherboard(self):
        for motherboard in self.__w.Win32_BaseBoard():
            if motherboard.SerialNumber:
                return motherboard.SerialNumber
        return None

    def _bios(self):
        for bios in self.__w.Win32_BIOS():
            if bios.SerialNumber:
                return bios.SerialNumber
        return None

    def _disk_serial(self):
        for disk in self.__w.Win32_DiskDrive():
            if disk.SerialNumber:
                return disk.SerialNumber
        return None

    def _machine_guid(self):
        try:
            target_key = winreg.OpenKey(self.__reg_conn, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(target_key, "MachineGuid")
            return value
        except Exception as e:
            print(f"Error {{MGUID}}: {e}")
            return None

    def _uuid(self):
        try:
            result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            uuid_output = result.stdout.strip()
            lines = [line.strip() for line in uuid_output.split('\n') if line.strip()]
            if len(lines) > 1:  # First line is header, second line should be UUID
                theUuid = lines[1]
                print(f"System UUID: {theUuid}")
                return theUuid
            else:
                print("UUID not found in output")
                return None
        except Exception as e:
            print(f"Error {{UUID}}: {e}")
            return None

    def _local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"Error {{Local IP}}: {e}")
            return None

    def _public_ip(self):
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to get public IP, status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error {{Public IP}}: {e}")
            return None