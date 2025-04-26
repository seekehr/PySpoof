import json
import sys
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
from utils.formats import ERROR
import machineid
import re
from utils.logger import Logger

# Comments powered by AI
class SystemInformation:
    def __init__(self, logger: Logger):
        # PC hardware identifiers
        self.__hostname = None
        self.__mac = None
        self.__motherboard = None
        self.__bios = None
        self.__processor_id = None
        self.__uuid = None
        self.__machineguid = None
        
        # Disk information
        self.__disk_serial = None
        self.__disk_model = None
        self.__volume_serial = None
        
        # OS information
        self.__installdate = None
        self.__os_serial = None
        self.__user_sid = None
        
        # Network information
        self.__local_ip = None
        self.__public_ip = None
        self.__wlan_guid = None
        self.__wlan_physical_address = None
        self.__wlan_bssid = None
        
        # Additional information
        self.__computersystem_properties = None
        self.__computersystem_length = None
        
        # Status flag
        self._loafded = False
        self.logger = logger

    async def load_system_info_async(self):
        """Load all system information asynchronously"""
        loop = asyncio.get_running_loop()

        # Group tasks by category for better organization
        tasks = {
            # PC Hardware
            'hostname': loop.run_in_executor(None, self._hostname),
            'mac': loop.run_in_executor(None, self._mac),
            'motherboard': loop.run_in_executor(None, self._motherboard),
            'bios': loop.run_in_executor(None, self._bios),
            'processor_id': loop.run_in_executor(None, self._processor_id),
            'uuid': loop.run_in_executor(None, self._uuid),
            'machineguid': loop.run_in_executor(None, self._machine_guid),
            
            # Disk
            'disk_serial': loop.run_in_executor(None, self._disk_serial),
            'disk_model': loop.run_in_executor(None, self._disk_model),
            'volume_serial': loop.run_in_executor(None, self._volumeserial),
            
            # OS
            'installdate': loop.run_in_executor(None, self._install_date),
            'os_serial': loop.run_in_executor(None, self._os_serial),
            'user_sid': loop.run_in_executor(None, self._user_sid),
            
            # Network
            'local_ip': loop.run_in_executor(None, self._local_ip),
            'public_ip': loop.run_in_executor(None, self._public_ip),
            'wlan_info': loop.run_in_executor(None, self._wlan_info),
            
            # Additional Info
            'computersystem_info': loop.run_in_executor(None, self._computersystem_info)
        }

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # Process results
        keys = list(tasks.keys())
        for i, key in enumerate(keys):
            result = results[i]
            if isinstance(result, Exception):
                # Task failed with exception
                self.logger.error(f"{ERROR} Task '{key}' failed: {result}")
                # Handle special cases
                if key == 'wlan_info':
                    self.__wlan_guid = None
                    self.__wlan_physical_address = None
                    self.__wlan_bssid = None
                elif key == 'computersystem_info':
                    self.__computersystem_properties = None
                    self.__computersystem_length = None
                else:
                    # Set corresponding attribute to None
                    private_attr_name = f'_{self.__class__.__name__}__{key}'
                    if hasattr(self, private_attr_name):
                        setattr(self, private_attr_name, None)
            elif key == 'wlan_info':
                # Process wlan_info dictionary result
                self.__wlan_guid = result.get('guid')
                self.__wlan_physical_address = result.get('physical_address')
                self.__wlan_bssid = result.get('bssid')
            elif key == 'computersystem_info':
                # Store length directly
                self.__computersystem_length = result
            else:
                # Standard attribute assignment
                private_attr_name = f'_{self.__class__.__name__}__{key}'
                if hasattr(self, private_attr_name):
                    setattr(self, private_attr_name, result)

        # Mark as loaded when complete
        self._loaded = True

    def get(self):
        output_str = ""
        try:
            # PC Section
            output_str += Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "PC" + Fore.YELLOW + "==============" + Fore.RESET + "\n"
            output_str += Fore.GREEN + "Hostname: " + Fore.RESET + (self.hostname or "Invalid Hostname") + "\n"
            output_str += Fore.GREEN + "Processor ID: " + Fore.RESET + (
                        self.processor_id or "Invalid Processor ID") + "\n"
            output_str += Fore.GREEN + "UUID: " + Fore.RESET + (self.uuid or "Invalid UUID") + "\n"
            output_str += Fore.GREEN + "Motherboard: " + Fore.RESET + (
                        self.motherboard or "Invalid Motherboard number") + "\n"
            output_str += Fore.GREEN + "BIOS: " + Fore.RESET + (self.bios or "Invalid BIOS number") + "\n"
            output_str += Fore.GREEN + "Machine GUID: " + Fore.RESET + (
                        self.machine_guid or "Invalid Machine GUID") + "\n"
            output_str += Fore.GREEN + "ComputerSystem Properties Count: " + Fore.RESET + (
                        str(self.computersystem_length) or "N/A") + "\n"

            output_str += Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "PC" + Fore.YELLOW + "==============" + Fore.RESET + "\n"
            if self.installdate:
                try:
                    timeStampToDate = datetime.datetime.strptime(self.installdate, '%Y%m%d%H%M%S')
                    output_str += Fore.GREEN + "Windows installed: " + Fore.RESET + str(
                        timeStampToDate) + " || " + self.installdate + "\n"
                except ValueError:
                    output_str += Fore.GREEN + "Windows installed: " + Fore.RESET + f"Invalid Date Format ({self.installdate})" + "\n"
            else:
                output_str += Fore.GREEN + "Windows installed: " + Fore.RESET + "Invalid Install Date" + "\n"
            output_str += Fore.GREEN + "OS Serial: " + Fore.RESET + (self.osserial or "Invalid OS Serial") + "\n"
            output_str += Fore.GREEN + "User SID: " + Fore.RESET + (self.user_sid or "Invalid User SID") + "\n"

            # Network Section
            output_str += Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "NET" + Fore.YELLOW + "==============" + Fore.RESET + "\n"
            output_str += Fore.GREEN + "General MAC: " + Fore.RESET + (self.mac or "Invalid MAC") + "\n"
            output_str += Fore.GREEN + "Local IP: " + Fore.RESET + (self.local_ip or "Invalid Local IP") + "\n"
            output_str += Fore.GREEN + "Public IP: " + Fore.RESET + (self.public_ip or "Invalid Public IP") + "\n"
            output_str += Fore.GREEN + "WLAN GUID: " + Fore.RESET + (self.wlan_guid or "N/A or Not Found") + "\n"
            output_str += Fore.GREEN + "WLAN Phys Addr: " + Fore.RESET + (
                        self.wlan_physical_address or "N/A or Not Found") + "\n"
            output_str += Fore.GREEN + "WLAN BSSID: " + Fore.RESET + (self.wlan_bssid or "N/A or Not Connected") + "\n"

            # Disk Section
            output_str += Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "DISK" + Fore.YELLOW + "==============" + Fore.RESET + "\n"
            output_str += Fore.GREEN + "Disk Serial: " + Fore.RESET + (self.disk_serial or "Invalid Serial") + "\n"
            output_str += Fore.GREEN + "Volume Serial: " + Fore.RESET + (
                        self.volume_serial or "Invalid Volume Serial") + "\n"
            output_str += Fore.GREEN + "Disk Model: " + Fore.RESET + (self.disk_model or "Invalid Disk Model") + "\n"

        except Exception as e:
            output_str += f"{ERROR} Could not self.logger.error. Error: {e}" + "\n"

        return output_str

    def log(self):
        """self.logger.error all system information in a formatted way"""
        output_str = self.get()
        print(output_str, end="")
        return output_str

    # ----------------------
    # Property getters
    # ----------------------
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

    @property
    def wlan_guid(self):
        return self.__wlan_guid

    @property
    def wlan_physical_address(self):
        return self.__wlan_physical_address

    @property
    def wlan_bssid(self):
        return self.__wlan_bssid

    @property
    def computersystem_length(self):
        return self.__computersystem_length

    # ----------------------
    # Data retrieval methods
    # ----------------------
    
    def _mac(self):
        """Get MAC address using uuid.getnode()"""
        try:
            node = uuid.getnode()
            mac_num = hex(node).replace('0x', '').upper()
            # Pad with leading zeros if necessary (MAC is 12 hex digits)
            mac_num = mac_num.zfill(12)
            
            # Ensure mac_num is exactly 12 chars before splitting
            if len(mac_num) == 12:
                mac_pairs = [mac_num[i: i + 2] for i in range(0, 12, 2)]
                mac = ':'.join(mac_pairs)  # Use colon as standard separator
                return mac
            else:
                self.self.logger.errorger.error(f"{ERROR} {{MAC}}: Processed hex value '{mac_num}' has unexpected length {len(mac_num)}.")
                return None
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{MAC}}: {e}")
            return None

    def _motherboard(self):
        """Get motherboard serial number using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                return board.SerialNumber.strip()
            return None  # No board found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Motherboard}}: {e}", sys.exc_info())
            return None

    def _bios(self):
        """Get BIOS serial number using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for bios in c.Win32_BIOS():
                return bios.SerialNumber.strip()
            return None  # No BIOS information found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{BIOS}}: {e}")
            return None

    def _disk_serial(self):
        """Get disk serial number using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                return disk.SerialNumber.strip()
            return None  # No disk found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Disk Serial}}: {e}")
            return None

    def _machine_guid(self):
        """Get machine GUID from registry"""
        try:
            # Attempt to get machine GUID from registry
            registry_path = r"SOFTWARE\Microsoft\Cryptography"
            value_name = "MachineGuid"

            with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    registry_path,
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            ) as registry_key:
                value, _ = winreg.QueryValueEx(registry_key, value_name)
                return value
        except Exception as e:
            self.logger.error(f"{ERROR} {{Machine GUID}}: {sys.exc_info()}")
            return None

    def _uuid(self):
        """Get system UUID using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for csproduct in c.Win32_ComputerSystemProduct():
                return csproduct.UUID
            return None  # No UUID found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{UUID}}: {e}")
            return None

    def _local_ip(self):
        """Get local IP address"""
        try:
            # Create a dummy connection to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Local IP}}: {e}")
            return None

    def _public_ip(self):
        """Get public IP address using external service"""
        try:
            # Try up to 3 different services to get public IP
            services = [
                "https://api.ipify.org",
                "https://ifconfig.me",
                "https://ip.seeip.org"
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue

            return None  # All services failed
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Public IP}}: {e}")
            return None

    def _install_date(self):
        """Get Windows installation date from registry"""
        try:
            # Get Windows installation date from registry
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            value_name = "InstallDate"

            with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            ) as registry_key:
                install_date_timestamp, _ = winreg.QueryValueEx(registry_key, value_name)

                # Convert UNIX timestamp to formatted date string
                install_date = datetime.datetime.fromtimestamp(install_date_timestamp)
                return install_date.strftime("%Y%m%d%H%M%S")
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Install Date}}: {e}")
            return None

    def _hostname(self):
        """Get system hostname"""
        try:
            return socket.gethostname()
        except Exception as e:
            self.logger.error(f"{ERROR} {{Hostname}}: {e}")
            return None

    def _os_serial(self):
        """Get Windows OS serial/product key"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            values_to_try = ["ProductId", "DigitalProductId"]

            with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            ) as registry_key:
                # Try each possible value name
                for value_name in values_to_try:
                    try:
                        value, _ = winreg.QueryValueEx(registry_key, value_name)
                        if value and isinstance(value, str):
                            return value.strip()
                    except:
                        continue
                return None  # No valid value found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{OS Serial}}: {e}")
            return None

    def _volumeserial(self):
        """Get volume serial number of C: drive"""
        try:
            # Get volume serial number of C: drive
            import ctypes
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
            serial_number = ctypes.c_ulong(0)
            max_component_length = ctypes.c_ulong(0)
            file_system_flags = ctypes.c_ulong(0)

            ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p("C:\\"),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                ctypes.pointer(serial_number),
                ctypes.pointer(max_component_length),
                ctypes.pointer(file_system_flags),
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer)
            )
            return str(serial_number.value)
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Volume Serial}}: {e}")
            return None

    def _processor_id(self):
        """Get processor ID using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for processor in c.Win32_Processor():
                return processor.ProcessorId.strip()
            return None  # No processor found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Processor ID}}: {e}")
            return None

    def _disk_model(self):
        """Get disk model using WMI"""
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                return disk.Model.strip()
            return None  # No disk found
        except Exception as e:
            self.self.logger.errorger.error(f"{ERROR} {{Disk Model}}: {e}")
            return None

    def _user_sid(self):
        """Get current user's SID using whoami command"""
        try:
            # Set up subprocess to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Common Windows encodings to try for decoding output
            encodings_to_try = ['utf-8', 'cp437', 'latin-1']
            
            # Run whoami command to get current user's SID
            process = subprocess.Popen(
                ['whoami', '/user'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                shell=False
            )
            stdout_bytes, stderr_bytes = process.communicate()

            # Check for command failure
            if process.returncode != 0:
                error_message = f"'whoami /user' command failed with return code {process.returncode}."
                # Try to decode stderr for more info
                stderr_decoded = None
                for enc in encodings_to_try:
                    try:
                        stderr_decoded = stderr_bytes.decode(enc)
                        error_message += f" Stderr ({enc}): {stderr_decoded.strip()}"
                        break
                    except UnicodeDecodeError:
                        continue
                        
                if not stderr_decoded:
                    error_message += " (Could not decode stderr)."
                    
                self.logger.error(f"{ERROR} {{User SID}}: {error_message}")
                return None

            # Try to decode stdout with various encodings
            output = None
            for enc in encodings_to_try:
                try:
                    output = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if output is None:
                self.logger.error(f"{ERROR} {{User SID}}: Could not decode 'whoami /user' output with tried encodings.")
                return None

            # Use regex to find the SID (S-1 followed by digits and hyphens)
            match = re.search(r"\b(S-1(?:-\d+)+)\s*$", output, re.MULTILINE)

            if match:
                return match.group(1)  # Return the captured SID
            else:
                # self.logger.error the actual output if parsing fails
                self.logger.error(f"{ERROR} {{User SID}}: Could not parse SID from 'whoami /user' output:\n---\n{output}\n---")
                return None

        except FileNotFoundError:
            self.logger.error(f"{ERROR} {{User SID}}: 'whoami' command not found. Ensure it is in the system PATH.")
            return None
        except Exception as e:
            self.logger.error(f"{ERROR} {{User SID}}: Unexpected error: {e}")
            return None

    def _wlan_info(self):
        """Get WLAN interface information (GUID, Physical Address, BSSID)"""
        # Initialize empty result dictionary
        wlan_info = {
            'guid': None,
            'physical_address': None,
            'bssid': None
        }
        self.logger.error_info = []

        try:
            # Set up subprocess to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Common Windows encodings to try
            encodings_to_try = ['utf-8', 'cp437', 'latin-1']
            output_decoded = None

            # Run netsh command to get WLAN interface info
            process = subprocess.Popen(
                ['netsh', 'wlan', 'show', 'interfaces'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                shell=False
            )
            stdout_bytes, stderr_bytes = process.communicate()

            # Check for command failure
            if process.returncode != 0:
                stderr_decoded = ""
                for enc in encodings_to_try:
                    try:
                        stderr_decoded = stderr_bytes.decode(enc).strip()
                        break
                    except UnicodeDecodeError:
                        continue
                        
                self.logger.error(f"{ERROR} {{WLAN Info}}: 'netsh wlan show interfaces' failed. Code: {process.returncode}. Stderr: {stderr_decoded or '(undecodable)'}")
                return wlan_info

            # Try to decode stdout with various encodings
            for enc in encodings_to_try:
                try:
                    output_decoded = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if not output_decoded:
                self.logger.error(f"{ERROR} {{WLAN Info}}: Could not decode 'netsh' output.")
                return wlan_info
            
            # Use regex to extract WLAN interface information
            # Updated GUID regex to match formats with or without braces
            guid_match = re.search(r"GUID\s+:\s+(?:\{)?([0-9a-fA-F\-]+)(?:\})?", output_decoded, re.IGNORECASE)
            pa_match = re.search(r"Physical address\s+:\s+((?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})", output_decoded, re.IGNORECASE)
            bssid_match = re.search(r"BSSID\s+:\s+((?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})", output_decoded, re.IGNORECASE)

            # Process and store extracted values
            if guid_match:
                wlan_info['guid'] = guid_match.group(1)
            else:
                self.logger.error_info.append("Could not find WLAN GUID.")

            if pa_match:
                # Normalize MAC to use consistent format
                wlan_info['physical_address'] = pa_match.group(1).replace(':', '-').upper()
            else:
                self.logger.error_info.append("Could not find WLAN Physical Address.")

            if bssid_match:
                # Normalize BSSID to use consistent format
                wlan_info['bssid'] = bssid_match.group(1).replace(':', '-').upper()
            else:
                # BSSID is often missing if not connected
                self.logger.error_info.append("Could not find WLAN BSSID (likely not connected).")

            # self.logger.error any missing information
            if self.logger.error_info:
                self.logger.error(f"[INFO] {{WLAN Info}}: {', '.join(self.logger.error_info)}")

            return wlan_info

        except FileNotFoundError:
            self.logger.error(f"{ERROR} {{WLAN Info}}: 'netsh' command not found. Ensure it is in the system PATH.")
            return wlan_info
        except Exception as e:
            self.logger.error(f"{ERROR} {{WLAN Info}}: Unexpected error: {e}")
            return wlan_info

    def _computersystem_info(self):
        """Get computer system properties using WMIC"""
        try:
            # Set up subprocess to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Run WMIC command to get computer system properties
            process = subprocess.Popen(
                ['wmic', 'computersystem', 'list', 'full'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                shell=False
            )
            stdout_bytes, stderr_bytes = process.communicate()
            
            # Check for command failure
            if process.returncode != 0:
                self.logger.error(f"{ERROR} {{ComputerSystem}}: WMIC command failed with return code {process.returncode}")
                return None
                
            # Try various encodings to decode the output
            encodings_to_try = ['utf-8', 'cp437', 'latin-1']
            output_decoded = None
            
            for enc in encodings_to_try:
                try:
                    output_decoded = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
                    
            if not output_decoded:
                self.logger.error(f"{ERROR} {{ComputerSystem}}: Could not decode WMIC output")
                return None
                
            # Parse the output into an array of properties
            properties = []
            lines = output_decoded.strip().split('\n')
            
            for line in lines:
                # Skip empty lines and CLASS line
                if not line.strip() or line.strip().startswith('CLASS'):
                    continue
                    
                # Extract property=value pairs
                if '=' in line:
                    property_name, value = line.strip().split('=', 1)
                    properties.append((property_name.strip(), value.strip()))
            
            # Store the properties array and its length
            self.__computersystem_properties = properties
            self.__computersystem_length = len(properties)
            
            return self.__computersystem_length
            
        except FileNotFoundError:
            self.logger.error(f"{ERROR} {{ComputerSystem}}: WMIC command not found. Ensure it is in the system PATH.")
            return None
        except Exception as e:
            self.logger.error(f"{ERROR} {{ComputerSystem}}: Unexpected error: {e}")
            return None