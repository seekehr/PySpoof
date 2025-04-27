import time

import pythoncom
import wmi

async def update_network(name, mac):
    time.sleep(3)
    pythoncom.CoInitialize()
    wm = wmi.WMI()
    for connection in wm.Win32_NetworkAdapter():
        if connection.ProductName == name:
            connection.MACAddress = mac