import asyncio
import re
import subprocess
import sys
import winreg

import pythoncom
import wmi
import sys
from colorama import Fore, Style
from system_information import SystemInformation
from utils.formats import *
from utils.generator import generate_random_values
from utils.update_wmi import update_network

adapter_base_key = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}'


async def spoof_mac(logger, sysinfo: SystemInformation):
    """
    Attempts to spoof the MAC address of the network adapter.
    """

    key = find_adapter_key(logger, sysinfo)
    if not key.startswith('000'):
        logger.error(f"Could not find adapter key in registry.")
        return None
    try:
        logger.inform(f"Spoofing MAC address...")
        current_mac = sysinfo.mac
        random_values = generate_random_values()
        if random_values.get("mac"):
            new_mac = random_values.get("mac")
        else:
            logger.error("Failed to generate random MAC address")
            return False

        pythoncom.CoInitialize()
        c = wmi.WMI()

        interface = None
        for connection in c.Win32_NetworkAdapter():
            if connection.MACAddress == current_mac:
                interface = connection.ProductName
        if interface:
            new_formatted_mac =  new_mac.upper().replace(':', '-')
            logger.debug(f"New formatted MAC: {new_formatted_mac}")
            logger.inform(f"Found interface '{interface}' for MAC address '{current_mac}'")
            try:
                # Set MAC address in registry
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                adapter_key_path = f"{adapter_base_key}\\{key}"
                adapter_key = winreg.OpenKey(reg, adapter_key_path, 0, winreg.KEY_ALL_ACCESS)

                winreg.SetValueEx(adapter_key, "NetworkAddress", 0, winreg.REG_SZ, new_formatted_mac)
                winreg.CloseKey(adapter_key)

                logger.inform(f"Successfully wrote new MAC '{new_formatted_mac}' to registry under {key}")

                # Disable the network adapter
                disable_command = f'powershell -Command "Get-NetAdapter | Where-Object {{ $_.InterfaceDescription -eq \\"{interface}\\" }} | Disable-NetAdapter -Confirm:$false"'
                logger.debug(f"Executing disable command")
                subprocess.run(disable_command, shell=True, check=True)
                logger.debug(f"Disabled interface with description'")

                # Enable the network adapter after changing the MAC address
                enable_command = f'powershell -Command "Get-NetAdapter | Where-Object {{ $_.InterfaceDescription -eq \\"{interface}\\" }} | Enable-NetAdapter -Confirm:$false"'
                logger.debug(f"Executing enable command: {enable_command}")
                subprocess.run(enable_command, shell=True, check=True)
                logger.debug(f"Enabled interface with description")

                await update_network(interface, new_mac)
                logger.debug("Successfully updated WMI for MAC.")

                return new_mac
            except subprocess.CalledProcessError as e:
                logger.error(f"PowerShell command failed during MAC spoofing: {e}", sys.exc_info())
            except Exception as e:
                logger.error(f"Error during MAC spoofing steps: {e}", sys.exc_info())
        else:
            logger.error(f"{ERROR}Could not find network interface for MAC address '{current_mac}'.{Style.RESET_ALL}")

    except Exception as e:
        logger.error(f"{ERROR}Failed to spoof MAC address.", sys.exc_info())

    return None

def find_adapter_key(logger, sysinfo: SystemInformation):
    """
    Finds the adapter key in the registry corresponding to the current MAC address.
    """
    try:
        logger.inform("Searching for adapter key in registry...")

        current_mac = sysinfo.mac
        pythoncom.CoInitialize()
        c = wmi.WMI()

        # Get the product name from the MAC address
        interface = None
        for connection in c.Win32_NetworkAdapter():
            if connection.MACAddress == current_mac:
                interface = connection.ProductName
                break

        if not interface:
            logger.error(f"{ERROR}Could not find network interface for MAC address '{current_mac}'.{Style.RESET_ALL}")
            return None

        logger.inform(f"Found interface '{interface}' for MAC address '{current_mac}'")

        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        class_key = winreg.OpenKey(reg, adapter_base_key)

        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(class_key, i)
                subkey_path = f"{adapter_base_key}\\{subkey_name}"
                subkey = winreg.OpenKey(reg, subkey_path)

                try:
                    driver_desc, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                    if driver_desc.strip() == interface.strip():
                        logger.inform(f"Matched interface '{interface}' with registry key '{subkey_name}'")
                        winreg.CloseKey(subkey)
                        winreg.CloseKey(class_key)
                        return subkey_name
                except FileNotFoundError:
                    logger.debug(f"DriverDesc not found in subkey '{subkey_name}'")

                winreg.CloseKey(subkey)
                i += 1

            except OSError:
                logger.warning("Reached end of registry entries without matching adapter.")
                break

        winreg.CloseKey(class_key)

    except Exception as e:
        logger.error(f"{ERROR}Failed to find adapter key.", sys.exc_info())

    return None
