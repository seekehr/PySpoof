import winreg
import subprocess
import sys

def verify_spoof_hostname(spoofed_name):
    try:
        # Registry path for the computer name
        reg_key_path = r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName"

        # Open the registry key in read-only mode
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path, 0, winreg.KEY_READ)

        # Retrieve the value of 'ComputerName' from the registry
        computer_name, _ = winreg.QueryValueEx(key, "ComputerName")

        # Close the registry key
        winreg.CloseKey(key)

        if spoofed_name == computer_name:
            return True
        else:
            return False
    except:
        return False




def verify_spoof_motherboard(spoofed_serial):
    try:
        # Run the WMIC command to get the BIOS serial number
        result = subprocess.run(
            ["wmic", "bios", "get", "serialnumber"],
            capture_output=True,
            text=True,
            check=True
        )

        # Extract the serial number from the output
        lines = result.stdout.strip().splitlines()
        if len(lines) >= 2:
            current_serial = lines[1].strip()
        else:
            return False  # Could not parse output

        # Compare the retrieved serial with the spoofed one
        if current_serial == spoofed_serial:
            return True
        else:
            return False

    except subprocess.CalledProcessError as e:
        # Command failed, probably WMIC missing or permissions issue
        return False
    except Exception:
        # Any other error
        return False
