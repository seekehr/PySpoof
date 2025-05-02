import winreg

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