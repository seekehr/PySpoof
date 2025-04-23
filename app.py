import asyncio
import platform
from systeminformation import SystemInformation
import winreg
import wmi
import time
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

start_time = time.time()

async def main():
    sys_info = SystemInformation()
    print("Starting to load system information asynchronously...")
    await sys_info.load_system_info_async()
    sys_info.print()
    print("Finished loading. Time:", time.time() - start_time)

if __name__ == "__main__":
    # On Windows, ProactorEventLoop is the default for asyncio,
    # which works well with the ThreadPoolExecutor used here.
    # For other platforms, the default event loop should also be fine.
    asyncio.run(main())




