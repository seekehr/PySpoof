import shutil
import sys
import tempfile
import threading
import time
import winreg
from os import mkdir

import pythoncom
import wmi

from listeners.update_info_listener import UpdateInfoListener
from spoofers import mac_spoofer, motherboard_spoof
from utils.generator import generate_random_values
from utils.formats import *
import subprocess
import os
from system_information import SystemInformation
from utils.logger import Logger
from config import Config

def pause_listener(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, threading.Thread):
                listener = getattr(arg, 'listener', None)
                if isinstance(listener, UpdateInfoListener):
                    listener.pause()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    if listener:
                        listener.resume()
    return wrapper


class Spoofer:
    def __init__(self, sys_info: SystemInformation, logger: Logger, config: Config):
        self._sys_info = sys_info
        self._logger = logger
        self._config = config
        self._random_values = generate_random_values()

    def create_registry_backup(self):
        """Create a backup of the registry before making any changes"""
        try:
            backup_path = "../resources/backup.reg"
            if self._config.has("backup_path"):
                backup_path = self._config.get("backup_path")
                if not backup_path.lower().endswith('.reg'):
                    backup_path += ".reg"

            # Ensure directory exists
            backup_dir = os.path.dirname(backup_path)
            os.makedirs(backup_dir, exist_ok=True)

            self._logger.inform(f"Creating registry backup at {backup_path}...")

            # Keys to back up
            keys_to_backup = [
                r"HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SystemInformation",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ComputerName",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\IDConfigDB",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\ACPI",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\PCI",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USB",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}",
                r"HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices"
            ]

            # Create a temporary directory for individual exports
            temp_dir = tempfile.mkdtemp()
            success_count = 0
            errors = 0
            failed_keys = []

            try:
                # Export each key to a temporary file
                for key in keys_to_backup:
                    # Create a safe filename from the registry key
                    key_name = key.replace('\\', '_').replace(':', '')
                    temp_file = os.path.join(temp_dir, f"{key_name}.reg")

                    command = f'reg export "{key}" "{temp_file}" /y'
                    process = subprocess.run(command, shell=True, capture_output=True, text=True)

                    if process.returncode != 0:
                        errors += 1
                        failed_keys.append(key)
                        self._logger.warn(f"Failed to backup {key}: {process.stderr}")
                    else:
                        success_count += 1
                        self._logger.success(f"Backed up {key}")

                # Combine all temporary files into one
                with open(backup_path, 'wb') as outfile:
                    # Write registry header
                    outfile.write(b'Windows Registry Editor Version 5.00\n\n')

                    # Append content from each successful export, skipping their headers
                    for key in keys_to_backup:
                        if key not in failed_keys:
                            key_name = key.replace('\\', '_').replace(':', '')
                            temp_file = os.path.join(temp_dir, f"{key_name}.reg")

                            with open(temp_file, 'rb') as infile:
                                # Skip the first two lines (header)
                                infile.readline()  # Windows Registry Editor Version 5.00
                                infile.readline()  # Empty line

                                # Copy the rest of the file
                                outfile.write(b'\n')
                                outfile.write(infile.read())

                if errors == 0:
                    self._logger.success(f"Registry backup created successfully at {backup_path}")
                    return True
                else:
                    self._logger.warn(
                        f"Registry backup completed with {errors} errors. {success_count} keys were backed up.")
                    return True  # Still returning true as partial backup is better than none

            finally:
                # Clean up temporary files
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            self._logger.error(f"Failed to create registry backup: {str(e)}", sys.exc_info())
            return False


    @pause_listener
    def spoof_hostname(self, oldName, thread: threading.Thread):
        new_hostname = generate_random_values()["hostname"]
        try:
            # Open registry key for computer name
            reg_key_path = r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path, 0, winreg.KEY_WRITE)

            # Change the computer name in the registry
            winreg.SetValueEx(key, "ComputerName", 0, winreg.REG_SZ, new_hostname)
            winreg.CloseKey(key)

            # Also change the ActiveComputerName value
            reg_key_path_active = r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path_active, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ActiveComputerName", 0, winreg.REG_SZ, new_hostname)
            winreg.CloseKey(key)
            return new_hostname

        except Exception as e:
            # Log the error with full exception details
            self._logger.error(f"Error occurred while changing hostname: {e}", sys.exc_info())
        return None

    @pause_listener
    def spoof_motherboard(self, thread: threading.Thread):
        return motherboard_spoof.spoof_motherboard(self._logger)

    @pause_listener
    def spoof_mac(self, thread: threading.Thread):
        return mac_spoofer.spoof_mac(self._logger, self._sys_info)