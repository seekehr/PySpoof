import platform
from systeminformation import SystemInformation
import winreg

import wmi
w = wmi.WMI()

reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)  # Connect to local machine's HKEY_LOCAL_MACHINE

if __name__ == "__main__":
    if platform.system() == "Windows" and reg_conn:
        si = SystemInformation(reg_conn)
        si.print()


