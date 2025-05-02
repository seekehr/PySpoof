import sys
import threading
import winreg
from os import mkdir

import wmi

from listeners.update_info_listener import UpdateInfoListener
from spoofers import mac_spoofer
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
            errors = 0
            backup_path = "../resources/backup.reg"
            if self._config.has("backup_path"):
                backup_path = self._config.get("backup_path") + ".reg"

            self._logger.inform(f"Creating registry backup at {backup_path}...")

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
                    errors += 1
                    self._logger.warn(f"Failed to backup {key}: {process.stderr}")
                else:
                    self._logger.success(f"Backed up {key}")

            if errors > 0: # todo
                with open(backup_path + ".reg", "w") as f:
                    f.write("")
                self._logger.success(f"Registry backup created at {backup_path}")
            else:
                self._logger.error(f"Failed to create registry backup.")

            return True
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()

            # The traceback object 'tb' contains information about the error location
            # tb.tb_lineno gives the line number where the exception occurred
            line_number = tb.tb_lineno

            # We can also get the filename if needed
            file_name = tb.tb_frame.f_code.co_filename
            self._logger.error(f"Failed to create registry backup.", sys.exc_info())
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
    def spoof_mac(self, thread: threading.Thread):
        return mac_spoofer.spoof_mac(self._logger, self._sys_info)