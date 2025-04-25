import json
import uuid
from tokenize import Number
from winreg import HKEYType
import subprocess
import datetime
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
import re # Import re for SID parsing

class SystemInformation:
    def __init__(self):
        self.__hostname = None
        self.__mac = None
        self.__motherboard = None
        self.__bios = None
        self.__disk_serial = None
        self.__machineguid = None
        self.__uuid = None
        self.__local_ip = None
        self.__public_ip = None
        self.__installdate = None
        self._loaded = False
        self.__os_serial = None
        self.__volume_serial = None
        self.__processor_id = None
        self.__disk_model = None
        self.__user_sid = None # Added user SID attribute

    async def load_system_info_async(self):
        loop = asyncio.get_running_loop()

        # Find all info asynchronously
        tasks = {
            'hostname': loop.run_in_executor(None, self._hostname),
            'mac': loop.run_in_executor(None, self._mac),
            'motherboard': loop.run_in_executor(None, self._motherboard),
            'bios': loop.run_in_executor(None, self._bios),
            'disk_serial': loop.run_in_executor(None, self._disk_serial),
            'machineguid': loop.run_in_executor(None, self._machine_guid),
            'uuid': loop.run_in_executor(None, self._uuid),
            'local_ip': loop.run_in_executor(None, self._local_ip),
            'public_ip': loop.run_in_executor(None, self._public_ip),
            'installdate': loop.run_in_executor(None, self._install_date),
            'os_serial': loop.run_in_executor(None, self._os_serial),
            'volume_serial': loop.run_in_executor(None, self._volumeserial),
            'processor_id': loop.run_in_executor(None, self._processor_id),
            'disk_model': loop.run_in_executor(None, self._disk_model),
            'user_sid': loop.run_in_executor(None, self._user_sid) # Added user SID task
        }

        results = await asyncio.gather(*tasks.values())

        keys = list(tasks.keys())
        for i, key in enumerate(keys):
            setattr(self, f'_{self.__class__.__name__}__{key}', results[i])
        self._loaded = True


    def print(self):
        try:
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "PC" + Fore.YELLOW + "==============" + Fore.RESET)
            print(Fore.GREEN + "Hostname: " + Fore.RESET + (self.hostname or "Invalid Hostname"))
            print(Fore.GREEN + "Processor ID: " + Fore.RESET + (self.processor_id or "Invalid Processor ID"))
            print(Fore.GREEN + "UUID: " + Fore.RESET + (self.uuid or "Invalid UUID"))
            print(Fore.GREEN + "Motherboard: " + Fore.RESET + (self.motherboard or "Invalid Motherboard number"))
            print(Fore.GREEN + "BIOS: " + Fore.RESET + (self.bios or "Invalid BIOS number"))
            print(Fore.GREEN + "Machine GUID: " + Fore.RESET + (self.machine_guid or "Invalid Machine GUID"))
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "os" + Fore.YELLOW + "==============" + Fore.RESET)
            if self.installdate: # Check if installdate is not None before parsing
                timeStampToDate = datetime.datetime.strptime(self.installdate, '%Y%m%d%H%M%S')
                print(Fore.GREEN + "Windows installed: " + Fore.RESET + str(timeStampToDate) + " || " + self.installdate)
            else:
                print(Fore.GREEN + "Windows installed: " + Fore.RESET + "Invalid Install Date")
            print(Fore.GREEN + "OS Serial: " + Fore.RESET + (self.osserial or "Invalid OS Serial"))
            print(Fore.GREEN + "User SID: " + Fore.RESET + (self.user_sid or "Invalid User SID")) # Added user SID print
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "NET" + Fore.YELLOW + "==============" + Fore.RESET)
            print(Fore.GREEN + "MAC Address: " + Fore.RESET + (self.mac or "Invalid MAC"))
            print(Fore.GREEN + "Local IP: " + Fore.RESET + (self.local_ip or "Invalid Local IP"))
            print(Fore.GREEN + "Public IP: " + Fore.RESET + (self.public_ip or "Invalid Public IP"))
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "DISK" + Fore.YELLOW + "==============" + Fore.RESET)
            print(Fore.GREEN + "Disk Serial: " + Fore.RESET + (self.disk_serial or "Invalid Serial"))
            print(Fore.GREEN + "Volume Serial: " + Fore.RESET + (self.volume_serial or "Invalid Volume Serial"))
            print(Fore.GREEN + "Disk Model: " + Fore.RESET + (self.disk_model or "Invalid Disk Model"))

        except Exception as e:
            print(f"{ERROR} Could not print. Error: {e}")


    @property
    def hostname(self):
        return self.__hostname

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

    @property
    def installdate(self):
        return self.__installdate

    @property
    def osserial(self):
        return self.__os_serial

    @property
    def volume_serial(self):
        return self.__volume_serial

    @property
    def processor_id(self):
        return self.__processor_id

    @property
    def disk_model(self):
        return self.__disk_model

    @property
    def user_sid(self):
        return self.__user_sid

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
            # Needed because WMI cannot run properly in a multi-threaded context without local initialization
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for motherboard in local_wmi.Win32_BaseBoard():
                if motherboard.SerialNumber:
                    pythoncom.CoUninitialize()
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
                    pythoncom.CoUninitialize()
                    return bios.SerialNumber
            return None
        except Exception as e:
            print(f"[ERROR] {{BIOS}}: {e}")
            return None

    def _disk_serial(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for disk in local_wmi.Win32_DiskDrive():
                if disk.SerialNumber:
                    pythoncom.CoUninitialize()
                    return disk.SerialNumber
            return None
        except Exception as e:
            print(f"[ERROR] {{DISK}}: {e}")
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
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for hardware in local_wmi.Win32_ComputerSystemProduct():
                if hardware.UUID:
                    pythoncom.CoUninitialize()
                    return hardware.UUID
            return None
        except Exception as e:
            print(f"[ERROR] {{DISK}}: {e}")
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

    def _install_date(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for hardware in local_wmi.Win32_OperatingSystem():
                if hardware.InstallDate:
                    pythoncom.CoUninitialize()
                    return hardware.InstallDate.split('.')[0]
            return None
        except Exception as e:
            print(f"{ERROR} {{DISK}}: {e}")
            return None

    def _hostname(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for system in local_wmi.Win32_ComputerSystem():
                if system.Name:
                    pythoncom.CoUninitialize()
                    return system.Name
            pythoncom.CoUninitialize()
            return None
        except Exception as e:
            pythoncom.CoUninitialize()
            print(f"{ERROR} {{HOSTNAME}}: {e}")
            return None

    def _os_serial(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for os in local_wmi.Win32_OperatingSystem():
                if os.SerialNumber:
                    pythoncom.CoUninitialize()
                    return os.SerialNumber
            return None
        except Exception as e:
            print(f"{ERROR} {{OS SERIAL}}: {e}")
            return None

    def _volumeserial(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for disk in local_wmi.Win32_LogicalDisk():
                if disk.VolumeSerialNumber:
                    pythoncom.CoUninitialize()
                    return disk.VolumeSerialNumber
            return None
        except Exception as e:
            print(f"{ERROR} {{VOLUME SERIAL}}: {e}")
            return None

    def _processor_id(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for processor in local_wmi.Win32_Processor():
                if processor.ProcessorId:
                    pythoncom.CoUninitialize()
                    return processor.ProcessorId
            return None
        except Exception as e:
            print(f"{ERROR} {{Processor ID}}: {e}")
            return None

    def _disk_model(self):
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            local_wmi = wmi.WMI()
            for disk in local_wmi.Win32_DiskDrive():
                if disk.Model:
                    pythoncom.CoUninitialize()
                    # WMIC might return extra spaces, strip them
                    return disk.Model.strip()
            pythoncom.CoUninitialize()
            return None
        except Exception as e:
            pythoncom.CoUninitialize()
            print(f"{ERROR} {{Disk Model}}: {e}")
            return None

    # Reverted back to subprocess for fetching User SID, using regex for parsing
    def _user_sid(self):
        try:
            # Execute the command and capture output
            # Hide console window popup
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Use shell=False if possible for security, works for whoami
            # Specify common encodings to try for decoding
            encodings_to_try = ['utf-8', 'cp437', 'latin-1']
            output = None
            stderr = None

            process = subprocess.Popen(['whoami', '/user'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       startupinfo=startupinfo,
                                       shell=False) 
            stdout_bytes, stderr_bytes = process.communicate()

            if process.returncode != 0:
                 error_message = f"'whoami /user' command failed with return code {process.returncode}."
                 for enc in encodings_to_try:
                     try:
                         stderr = stderr_bytes.decode(enc)
                         error_message += f" Stderr ({enc}): {stderr.strip()}"
                         break # Stop decoding on success
                     except UnicodeDecodeError:
                         continue
                 print(f"{ERROR} {{User SID}}: {error_message}")
                 return None

            # Attempt to decode stdout using different encodings
            for enc in encodings_to_try:
                try:
                    output = stdout_bytes.decode(enc)
                    break # Stop decoding on success
                except UnicodeDecodeError:
                    continue
            
            if output is None:
                print(f"{ERROR} {{User SID}}: Could not decode 'whoami /user' output with tried encodings.")
                return None

            # Use regex to find the SID (S-1- followed by digits and hyphens)
            # This looks for the SID pattern at the end of a line, potentially preceded by whitespace
            match = re.search(r"\b(S-1(?:-\d+)+)\s*$", output, re.MULTILINE)

            if match:
                return match.group(1) # Return the captured SID string
            else:
                print(f"{ERROR} {{User SID}}: Could not parse SID from whoami output:\n{output}")
                return None
        
        except FileNotFoundError:
            print(f"{ERROR} {{User SID}}: 'whoami' command not found. Ensure it's in the system PATH.")
            return None
        except Exception as e:
            print(f"{ERROR} {{User SID}}: Unexpected error: {e}")
            return None