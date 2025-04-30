import json
import argparse
import asyncio
import atexit
import ctypes
import os
import sys
import threading
import time
from threading import Thread

from colorama import Fore, Style
from colorama import init

from config import Config
from listeners.update_info_listener import UpdateInfoListener
from spoofers.spoofer import Spoofer
from system_information import SystemInformation
from utils.formats import ERROR, SUCCESS
from utils.logger import Logger
start_time = time.time()
init(autoreset=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.error(f"{ERROR} while loading: {e}", sys.exc_info())
        exit(1)

if not is_admin():
    print("Please run this script as an administrator.")
    exit(1)

def dirsAndFiles():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("resources", exist_ok=True)
    with open("resources/config.json", "w") as f:
        f.write(json.dumps({}))
dirsAndFiles()

logger = Logger(os.path.join("logs", "system_logs.txt"))
config = Config(logger)
output = False


async def handle_args(sys_info, log) -> Thread|None:
    parser = argparse.ArgumentParser(description="Process some flags.")
    parser.add_argument('--o', action='store_true', help="Enable saving output to the default file (output.txt)")
    parser.add_argument('--spoof', action='store_true', help="Run in spoofer mode")
    parser.add_argument("--listen", action="store_true", help="Enable listening for system information updates")
    args = parser.parse_args()
    default_output_filename = "resources/output.txt"

    if args.o:
        config.set("output", default_output_filename)
        log.inform(f"Output saving enabled by --o flag. Output will be saved to: {default_output_filename}")
    else:
        current_config_output = config.get("output")
        if isinstance(current_config_output, str) and current_config_output.lower().endswith(".txt"):
            log.inform(f"Output saving enabled by config. Using output file: {current_config_output}")

    thread = None
    if args.spoof:
        await spoofHandleArgs(args, sys_info)
    if args.listen:
        thread = listenHandleArgs(args, sys_info)

    return thread

async def spoofHandleArgs(args, sys_info: SystemInformation):
    if args.spoof:
        spoofer = Spoofer(sys_info, logger, config)
        await start_interactive_cli(spoofer, sys_info)
        exit(1)

def listenHandleArgs(args, sys_info) -> Thread | None:
    listen = False
    if args.listen:
        listen = True
    else:
        current_config_output = config.get("listen")
        if isinstance(current_config_output, str) and current_config_output.lower().endswith("true"):
            logger.inform(f"Listener enabled by config")
            listen = True

    if listen:
        logger.inform("Listening for system information updates...")
        listener = UpdateInfoListener(sys_info, logger)
        listener_thread = threading.Thread(target=listener.run, daemon=False)
        listener_thread.start()
        return listener_thread
    return None


# ==== Main ==== (bro im so sweepy) #
async def main():
    try:
        sys_info = SystemInformation(logger)
        thread = await handle_args(sys_info, logger)
        logger.inform("Starting to load system information asynchronously...\n")
        print(sys_info.get())
        logger.log("\nFinished loading. Time: " + str(time.time() - start_time) + " seconds")
        while thread.is_alive():
            logger.inform("Listening for updates...")
            time.sleep(15)
    except Exception as e:
        logger.inform(f"{ERROR}: {e}")
        exit(1)

# ==== Spoofer =====
async def start_interactive_cli(spoofer, sys_info): # Assuming spoofer object has methods create_registry_backup and spoof_mac
    try:
        backup = False
        # Check if the backup file exists
        backup_path = config.get("backup_path") + ".reg"
        if backup_path and os.path.exists(backup_path):
            backup = True
            logger.inform(f"Existing backup found at {backup_path}.{Style.RESET_ALL}")
        else:
             logger.warn(f"No existing backup found at {backup_path}. Please create a backup before spoofing.{Style.RESET_ALL}")

        while True:
            command = input(f"{Fore.CYAN}Spoofing CLI> {Style.RESET_ALL}").lower()  # Get input and convert to lowercase
            match command:
                case "exit":
                    logger.inform(f"{SUCCESS}Exiting spoofing mode...{Style.RESET_ALL}")
                    break  # Exit the loop
                case "help":
                    logger.log("Available commands:")
                    logger.log(" mac     - Start the MAC address spoofing")
                    logger.log(" backup  - Create a registry backup")
                    logger.log(" exit    - Exit the spoofing mode")
                case "mac":
                    if not backup:
                        logger.warn(f"Backup not created! Run 'backup' command first.{Style.RESET_ALL}")
                        continue
                    # Assuming spoofer.spoof_mac() is an async operation if the cli is async
                    # If not, you might need await spoofer.spoof_mac() if spoof_mac is an awaitable
                    oldMac = sys_info.mac
                    result = await spoofer.spoof_mac()
                    if result:
                        logger.log(f"{Fore.GREEN}Old MAC: {Fore.RESET}{oldMac}")
                        logger.log(f"{Fore.GREEN}New MAC: {Fore.RESET}{sys_info.updated_mac}")
                        while True:
                            logger.log("MAC: " + sys_info.mac)
                            time.sleep(3)
                case "backup":
                    logger.inform(f"{Fore.YELLOW}Creating registry backup...{Style.RESET_ALL}")
                    # Assuming spoofer.create_registry_backup() is an async operation
                    # If not, you might need await spoofer.create_registry_backup() if create_registry_backup is an awaitable
                    spoofer.create_registry_backup()
                    backup = True
                    logger.inform(f"{SUCCESS}Backup created successfully.{Style.RESET_ALL}")
                case "info":
                    sys_info.log()
                case _:  # Wildcard case for any other input
                    logger.error(f"{ERROR} Unknown command: {command}{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{ERROR}Error found during spoofing:{Style.RESET_ALL}", sys.exc_info())


def cleanup_function():
    logger.save()
    config.save()

# Register the cleanup function
atexit.register(cleanup_function)

if __name__ == "__main__":
    asyncio.run(main())
