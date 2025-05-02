import os
import subprocess
import threading
import winreg
import sys

from utils.generator import generate_random_values


def spoof_motherboard(logger):
    try:
        new_serial = generate_random_values()['motherboard']
        # Try to spoof registry values for motherboard serial number
        if not _spoof_motherboard_registry(logger, new_serial):
            logger.error("Failed to spoof motherboard serial number in registry.")
            return None

        # Try to spoof WMI BIOS serial number using MOF override
        if not _spoof_bios_serial_wmi(logger, new_serial):
            logger.error("Failed to spoof BIOS serial number in WMI.")
            return None

        logger.debug(f"Successfully spoofed motherboard and BIOS serial numbers.")
        return new_serial

    except Exception as e:
        logger.error(f"An error occurred while spoofing motherboard serial: {str(e)}", sys.exc_info())
        return None


def _spoof_motherboard_registry(logger, new_serial):
    # Registry paths that may contain motherboard information
    registry_paths = [
        (r"SYSTEM\CurrentControlSet\Control\SystemInformation", "BaseBoardSerialNumber"),
        (r"HARDWARE\DESCRIPTION\System\BIOS", "BaseBoardSerialNumber"),
        (r"HARDWARE\DESCRIPTION\System\BIOS", "SerialNumber")
    ]

    success_count = 0
    for path, value_name in registry_paths:
        try:
            # Try to open and modify each registry key
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)

            # Set the new value
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, new_serial)
            winreg.CloseKey(key)

            logger.debug(f"Successfully modified {value_name} in {path}")
            success_count += 1

        except Exception as e:
            logger.error(f"Failed to modify {path}\\{value_name}: {str(e)}")

    return success_count > 0


def _spoof_bios_serial_wmi(logger, new_serial):
    mof_file = "resources/bios_override.mof"

    try:
        # Compile the MOF file using mofcomp to register the new class in WMI
        subprocess.run(["mofcomp", mof_file], check=True)
        logger.debug(f"Successfully spoofed BIOS serial using {mof_file}.")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"mofcomp failed with exit code {e.returncode}: {e.output}")
        return False

    except Exception as e:
        logger.error(f"Failed to spoof BIOS serial in WMI: {str(e)}")
        return False
## Failed project.