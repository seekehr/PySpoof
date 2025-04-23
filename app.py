import platform
from systeminformation import SystemInformation
import winreg
import wmi
import time
from colorama import Fore, Back, Style

start_time = time.time()
w = wmi.WMI()

reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)  # Connect to local machine's HKEY_LOCAL_MACHINE

if __name__ == "__main__":
    if platform.system() == "Windows" and reg_conn:
        i = 0
        for i in range(10):
            si = SystemInformation(reg_conn)
            si.print()
            execution_time = time.time() - start_time
        print(f"{Fore.RED}Execution time{Fore.RESET}:{execution_time}")





