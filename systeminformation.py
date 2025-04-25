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
import re

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
        self.__user_sid = None
        # WLAN Info Attributes
        self.__wlan_guid = None
        self.__wlan_physical_address = None
        self.__wlan_bssid = None
        # Computer system properties
        self.__computersystem_properties = None
        self.__computersystem_length = None

    async def load_system_info_async(self):
        loop = asyncio.get_running_loop()

        # --- Individual info tasks ---
        tasks = {
            'hostname': loop.run_in_executor(None, self._hostname),
            'mac': loop.run_in_executor(None, self._mac), # General MAC (usually Ethernet first)
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
            'user_sid': loop.run_in_executor(None, self._user_sid),
            # --- Combined WLAN info task ---
            'wlan_info': loop.run_in_executor(None, self._wlan_info), # Fetches Guid, Phys Addr, BSSID together
            # --- Computer system properties ---
            'computersystem_info': loop.run_in_executor(None, self._computersystem_info)
        }

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks.values(), return_exceptions=True) # Handle potential exceptions

        # Process results
        keys = list(tasks.keys())
        for i, key in enumerate(keys):
            result = results[i]
            if isinstance(result, Exception):
                print(f"{ERROR} Task '{key}' failed: {result}")
                # Set corresponding attributes to None or keep default
                if key == 'wlan_info':
                    self.__wlan_guid = None
                    self.__wlan_physical_address = None
                    self.__wlan_bssid = None
                elif key == 'computersystem_info':
                    self.__computersystem_properties = None
                    self.__computersystem_length = None
                else:
                     setattr(self, f'_{self.__class__.__name__}__{key}', None)
            elif key == 'wlan_info':
                # Distribute results from the combined WLAN task
                self.__wlan_guid = result.get('guid')
                self.__wlan_physical_address = result.get('physical_address')
                self.__wlan_bssid = result.get('bssid')
            elif key == 'computersystem_info':
                self.__computersystem_length = result
            else:
                setattr(self, f'_{self.__class__.__name__}__{key}', result)

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
            print(Fore.GREEN + "ComputerSystem Properties Count: " + Fore.RESET + (str(self.computersystem_length) or "N/A"))
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "os" + Fore.YELLOW + "==============" + Fore.RESET)
            if self.installdate: # Check if installdate is not None before parsing
                timeStampToDate = datetime.datetime.strptime(self.installdate, '%Y%m%d%H%M%S')
                print(Fore.GREEN + "Windows installed: " + Fore.RESET + str(timeStampToDate) + " || " + self.installdate)
            else:
                print(Fore.GREEN + "Windows installed: " + Fore.RESET + "Invalid Install Date")
            print(Fore.GREEN + "OS Serial: " + Fore.RESET + (self.osserial or "Invalid OS Serial"))
            print(Fore.GREEN + "User SID: " + Fore.RESET + (self.user_sid or "Invalid User SID"))
            print(Fore.YELLOW + "==============" + Fore.LIGHTMAGENTA_EX + "NET" + Fore.YELLOW + "==============" + Fore.RESET)
            print(Fore.GREEN + "General MAC: " + Fore.RESET + (self.mac or "Invalid MAC")) # Renamed for clarity
            print(Fore.GREEN + "WLAN GUID: " + Fore.RESET + (self.wlan_guid or "N/A or Not Found"))
            print(Fore.GREEN + "WLAN Phys Addr: " + Fore.RESET + (self.wlan_physical_address or "N/A or Not Found"))
            print(Fore.GREEN + "WLAN BSSID: " + Fore.RESET + (self.wlan_bssid or "N/A or Not Connected"))
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
        # This returns the MAC from uuid.getnode(), often Ethernet but not guaranteed
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

    # WLAN Properties
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

    # --- Data Fetching Methods ---
    def _mac(self):
        try:
            node = uuid.getnode()
            mac_num = hex(node).replace('0x', '').upper()
            # Pad with leading zeros if necessary (MAC is 12 hex digits)
            mac_num = mac_num.zfill(12)
            # Debug prints (temporary)
            # print(f"DEBUG [MAC]: node={node}, hex={hex(node)}, mac_num={mac_num}")
            # Ensure mac_num is exactly 12 chars before splitting
            if len(mac_num) == 12:
                mac_pairs = [mac_num[i: i + 2] for i in range(0, 12, 2)]
                # print(f"DEBUG [MAC]: pairs={mac_pairs}")
                mac = ':'.join(mac_pairs) # Use colon as standard separator
                return mac
            else:
                print(f"{ERROR} {{MAC}}: Processed hex value '{mac_num}' has unexpected length {len(mac_num)}.")
                return None
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

            # Use regex to find the SID (S-1 followed by digits and hyphens)
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

    # Added WLAN info method (fetches Guid, Phys Addr, BSSID together)
    def _wlan_info(self):
        wlan_info = {}
        log_info = []

        try:
            # Execute the command and capture output, hide console
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            encodings_to_try = ['utf-8', 'cp437', 'latin-1']
            output_decoded = None

            process = subprocess.Popen(['netsh', 'wlan', 'show', 'interfaces'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       startupinfo=startupinfo,
                                       shell=False)
            stdout_bytes, stderr_bytes = process.communicate()

            if process.returncode != 0:
                # Try to decode stderr for a better error message
                stderr_decoded = ""
                for enc in encodings_to_try:
                    try:
                        stderr_decoded = stderr_bytes.decode(enc).strip()
                        break
                    except UnicodeDecodeError:
                        continue
                print(f"{ERROR} {{WLAN Info}}: 'netsh wlan show interfaces' failed. Code: {process.returncode}. Stderr: {stderr_decoded or '(undecodable)'}")
                return wlan_info # Return empty dict on failure

            # Try decoding stdout
            for enc in encodings_to_try:
                try:
                    output_decoded = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if not output_decoded:
                print(f"{ERROR} {{WLAN Info}}: Could not decode 'netsh' output.")
                return wlan_info
            
            # Use regex to find the required fields
            # Assuming only one active WLAN interface shown, or taking the first one
            guid_match = re.search(r"GUID\s+:\s+(?:\{)?([0-9a-fA-F\-]+)(?:\})?", output_decoded, re.IGNORECASE)
            pa_match = re.search(r"Physical address\s+:\s+((?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})", output_decoded)
            bssid_match = re.search(r"BSSID\s+:\s+((?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})", output_decoded)

            if guid_match:
                wlan_info['guid'] = guid_match.group(1)
            else:
                log_info.append("Could not find WLAN GUID.")
            if pa_match:
                 # Normalize MAC to use hyphens like uuid.getnode()
                wlan_info['physical_address'] = pa_match.group(1).replace(':', '-').upper()
            else:
                 log_info.append("Could not find WLAN Physical Address.")
            if bssid_match:
                # Normalize BSSID to use hyphens and uppercase
                wlan_info['bssid'] = bssid_match.group(1).replace(':', '-').upper()
            else:
                # BSSID is often missing if not connected, this is usually expected
                log_info.append("Could not find WLAN BSSID (likely not connected).")
 
            # Print collected info messages if any fields were missing
            if log_info:
                print(f"[INFO] {{WLAN Info}}: {', '.join(log_info)}")

            return wlan_info

        except FileNotFoundError:
            print(f"{ERROR} {{WLAN Info}}: 'netsh' command not found. Ensure it's in the system PATH.")
            return wlan_info
        except Exception as e:
            print(f"{ERROR} {{WLAN Info}}: Unexpected error: {e}")
            return wlan_info # Return empty dict on unexpected error

    # Get computer system properties using WMIC and return the array length
    def _computersystem_info(self):
        try:
            # Set up subprocess to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Run the WMIC command
            process = subprocess.Popen(['wmic', 'computersystem', 'list', 'full'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     startupinfo=startupinfo,
                                     shell=False)
            
            stdout_bytes, stderr_bytes = process.communicate()
            
            if process.returncode != 0:
                print(f"{ERROR} {{ComputerSystem}}: WMIC command failed with return code {process.returncode}")
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
                print(f"{ERROR} {{ComputerSystem}}: Could not decode WMIC output")
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
            print(f"{ERROR} {{ComputerSystem}}: WMIC command not found. Ensure it is in the system PATH.")
            return None
        except Exception as e:
            print(f"{ERROR} {{ComputerSystem}}: Unexpected error: {e}")
            return None