import json
import uuid
from winreg import HKEYType
import subprocess

import pythoncom
import wmi
import winreg
import socket
import requests
from colorama import Fore, Back, Style
import asyncio
import concurrent.futures
from utils.ERROR import ERROR
import machineid

class SystemInformation:
    def __init__(self):
        self.__w = wmi.WMI()
        self.__mac = None
        self.__motherboard = None
        self.__bios = None
        self.__disk_serial = None
        self.__machineguid = None
        self.__uuid = None
        self.__local_ip = None
        self.__public_ip = None
        self._loaded = False

    async def load_system_info_async(self):
        loop = asyncio.get_running_loop()

        tasks = {
            'mac': loop.run_in_executor(None, self._mac),
            'motherboard': loop.run_in_executor(None, self._motherboard),
            'bios': loop.run_in_executor(None, self._bios),
            'disk_serial': loop.run_in_executor(None, self._disk_serial),
            'machineguid': loop.run_in_executor(None, self._machine_guid),
            'uuid': loop.run_in_executor(None, self._uuid),
            'local_ip': loop.run_in_executor(None, self._local_ip),
            'public_ip': loop.run_in_executor(None, self._public_ip),
        }

        results = await asyncio.gather(*tasks.values())

        keys = list(tasks.keys())
        for i, key in enumerate(keys):
            setattr(self, f'_{self.__class__.__name__}__{key}', results[i])
        self._loaded = True

    def print(self):
        print(Fore.GREEN + "MAC: " + Fore.RESET + (self.mac or "Invalid MAC"))
        print(Fore.GREEN + "Motherboard: " + Fore.RESET + (self.motherboard or "Invalid Motherboard number"))
        print(Fore.GREEN + "BIOS: " + Fore.RESET + (self.bios or "Invalid BIOS number"))
        print(Fore.GREEN + "DISK Serial: " + Fore.RESET + (self.disk_serial or "Invalid Serial"))
        print(Fore.GREEN + "Machine GUID: " + Fore.RESET + (self.machine_guid or "Invalid Machine GUID"))
        print(Fore.GREEN + "UUID: " + Fore.RESET + (self.uuid or "Invalid UUID"))
        print(Fore.GREEN + "Local IP: " + Fore.RESET + (self.local_ip or "Invalid Local IP"))
        print(Fore.GREEN + "Public IP: " + Fore.RESET + (self.public_ip or "Invalid Public IP"))

    @property
    def loaded(self):
        return self._loaded

    @property
    def mac(self):
        return self.__mac

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

    # --- Existing data fetching methods (remain largely unchanged) ---

    def _mac(self):
        try:
            mac_num = hex(uuid.getnode()).replace('0x', '').upper()
            mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
            return mac
        except Exception as e:
            print(f"{ERROR} {{MAC}}: {e}")
            return None

    def _motherboard(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for motherboard in local_wmi.Win32_BaseBoard():
                if motherboard.SerialNumber:
                    return motherboard.SerialNumber
            return None
        except Exception as e:
            print(f"{ERROR} {{Motherboard}}: {e}")
            return None

    def _bios(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for bios in local_wmi.Win32_BIOS():
                if bios.SerialNumber:
                    return bios.SerialNumber
            return None
        except Exception as e:
            print(f"[ERROR] {{BIOS}}: {e}")
            return None

    def _disk_serial(self):
        try:
            result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            uuid_output = result.stdout.strip()
            lines = [line.strip() for line in uuid_output.split('\n') if line.strip()]
            if len(lines) > 1:  # First line is header, second line should be UUID
                serialNumber = lines[1]
                return serialNumber
            else:
                print(f"{ERROR} Serial Number not found in output")
                return None
        except Exception as e:
            print(f"{ERROR} {{UUID}}: {e}")
            return None

    def _machine_guid(self):
        try:
            reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            if reg_conn:
                target_key = winreg.OpenKey(reg_conn, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ)
                value, regtype = winreg.QueryValueEx(target_key, "MachineGuid")
                reg_conn.Close()
                return value
            return None
        except Exception as e:
            print(f"{ERROR} {{MGUID}}: {e}")
            return None

    def _uuid(self):
        try:
            result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW) # Added flag to hide window
            uuid_output = result.stdout.strip()
            lines = [line.strip() for line in uuid_output.split('\n') if line.strip()]
            if len(lines) > 1:  # First line is header, second line should be UUID
                theUuid = lines[1]
                return theUuid
            else:
                print("UUID not found in output")
                return None
        except Exception as e:
            print(f"{ERROR} {{UUID}}: {e}")
            return None

    def _local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"{ERROR} {{Local IP}}: {e}")
            return None

    def _public_ip(self):
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to get public IP, status code: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"{ERROR} {{Public IP}}: Request timed out")
            return None
        except Exception as e:
            print(f"{ERROR} {{Public IP}}: {e}")
            return None