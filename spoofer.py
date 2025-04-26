from utils.generator import generate_random_values
from utils.formats import *
import subprocess
import os
from systeminformation import SystemInformation
from utils.logger import Logger

class Spoofer():
    def __init__(self, sys_info: SystemInformation, logger: Logger):
        self._sys_info = sys_info
        self._logger = Logger
        self._random_values = generate_random_values()

    def create_registry_backup(self):
        """Create a backup of the registry before making any changes"""
        try:
            backup_path = os.path.join(os.getcwd(), "resources/backup.reg")
            log(f"{INFO} Creating registry backup at {backup_path}...")

            # Keys to back up
            keys_to_backup = [
                r"HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SystemInformation",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ComputerName",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            ]

            # Create the backup using reg.exe
            for key in keys_to_backup:
                command = f'reg export "{key}" "{backup_path}" /y'
                process = subprocess.run(command, shell=True, capture_output=True, text=True)

                if process.returncode != 0:
                    (f"{WARNING} Failed to backup {key}: {process.stderr}")
                else:
                    log(f"{SUCCESS} Backed up {key}")

            log(f"{SUCCESS} Registry backup created at {backup_path}")
            return True
        except Exception as e:
            log(f"{ERROR} Failed to create registry backup: {e}")
            return False

    def spoof_mac(self):
        try:
           current_mac = self._sys_info.mac
           new_mac = self._random_values.mac

           def get_interface_name(mac_address):
               # Run PowerShell command to filter by MAC address
               command = f'powershell Get-NetAdapter | Where-Object {{ $_.MacAddress -eq "{mac_address}" }}'
               result = subprocess.check_output(command, shell=True, text=True)

               # If result is not empty, return the interface name
               if result:
                   # Extract the interface name from the result
                   lines = result.splitlines()
                   for line in lines:
                       if "Name" in line:  # Name of the interface is usually labeled as 'Name'
                           interface_name = line.split(":")[1].strip()
                           return interface_name
               return None

           interface = get_interface_name(current_mac)
           subprocess.call(f'powershell Set-NetAdapter -Name "{interface}" -MacAddress "{new_mac}"', shell=True)
           subprocess.call(f'powershell Disable-NetAdapter -Name "{interface}" -Confirm:$false', shell=True)
           subprocess.call(f'powershell Enable-NetAdapter -Name "{interface}"', shell=True)
        except Exception as e:
            log(f"{ERROR} Failed to spoof MAC address: {e}")