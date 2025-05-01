import queue
import json
import argparse
import asyncio
import atexit
import ctypes
import os
import sys
import threading
import time
from argparse import Namespace
from threading import Thread
from typing import Any, Coroutine

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
    config_path = "resources/config.json"
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(json.dumps({}))
dirsAndFiles()

logger = Logger(os.path.join("logs", "system_logs.txt"))
config = Config(logger)
output = False
spoofing = False
thread: Thread|None = None

async def handle_args(sys_info, logger) -> Namespace:
    parser = argparse.ArgumentParser(description="Process some flags.")
    parser.add_argument('--o', action='store_true', help="Enable saving output to the default file (output.txt)")
    parser.add_argument('--spoof', action='store_true', help="Run in spoofer mode")
    parser.add_argument("--listen", action="store_true", help="Enable listening for system information updates")
    args = parser.parse_args()
    default_output_filename = "resources/output.txt"

    tasks = []
    tasks.append(outputHandleArgs(args, sys_info))
    tasks.append(listenHandleArgs(args, sys_info))
    tasks.append(spoofHandleArgs(args, sys_info))

    if tasks:
        await asyncio.gather(*tasks)

    return args

async def outputHandleArgs(args, sys_info: SystemInformation):
    if args.o:
        config.set("output", default_output_filename)
        logger.inform(f"Output saving enabled by --o flag. Output will be saved to: {default_output_filename}")
    else:
        current_config_output = config.get("output")
        if isinstance(current_config_output, str) and current_config_output.lower().endswith(".txt"):
            logger.inform(f"Output saving enabled by config. Using output file: {current_config_output}")
        else:
            config.set("output", default_output_filename)
            config.save()
            logger.inform(f"Output disabled by config. Initialised confing using output file: {default_output_filename}")

async def spoofHandleArgs(args, sys_info: SystemInformation):
    global spoofing
    if args.spoof:
        spoofing = True

async def listenHandleArgs(args, sys_info) -> Thread | None:
    global thread
    listen = False
    if args.listen:
        listen = True
        config.set("listen", "true")
        config.save()
    else:
        current_config_output = config.get("listen")
        if isinstance(current_config_output, str) and current_config_output.lower() == "true":
            logger.inform(f"Listener enabled by config")
            listen = True
        else:
            config.set("listen", "false")
            config.save()
    
    if listen:
        logger.debug("Starting listener thread")
        listener = UpdateInfoListener(sys_info, logger)
        thread = threading.Thread(target=listener.run, daemon=True)
        thread._listener = listener  # Store listener instance as an attribute of the thread
        thread.start()
        return thread
    return None

# ==== Main ==== (bro im so sweepy) #
async def main():
    global spoofing
    global thread
    sys_info = SystemInformation(logger)
    info = sys_info.get()
    sys_info.update()
    try:
        args = await handle_args(sys_info, logger)

        logger.log(info)
        
        tasks = []
        # Check if listener thread was created during handle_args
        if thread is not None:
            async def monitor_thread():
                while thread.is_alive():
                    await asyncio.sleep(5)
                logger.debug("Listener thread stopped")
            tasks.append(monitor_thread())

        if spoofing:
            spoofer = Spoofer(sys_info, logger, config)
            tasks.append(start_interactive_cli(spoofer, sys_info))

        # Run all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)
        
        logger.log("\nFinished loading. Time: " + str(time.time() - start_time) + " seconds")

    except Exception as e:
        logger.inform(f"{ERROR}: {e}")
        exit(1)


# ==== Spoofer =====
async def start_interactive_cli(spoofer, sys_info): # Assuming spoofer object has methods create_registry_backup and spoof_mac
    logger.debug("Starting interactive CLI")
    try:
        backup = False
        # Check if the backup file exists
        backup_path = config.get("backup_path") + ".reg"
        if backup_path and os.path.exists(backup_path):
            backup = True
            logger.inform(f"Existing backup found at {backup_path}.{Style.RESET_ALL}")
        else:
             logger.warn(f"No existing backup found at {backup_path}. Please create a backup before spoofing.{Style.RESET_ALL}")


        # Queue in the main thread
        input_queue = queue.Queue()
        
        run_input = True
        
        # Input reader in another thread that updates queue on the main thread to allow other output (specifically listener) to run
        def input_reader():
            while run_input:
                try:
                    line = input(f"{Fore.CYAN}Spoofing CLI> {Style.RESET_ALL}")
                    input_queue.put(line.lower())
                except EOFError:
                    break
        
        input_thread = threading.Thread(target=input_reader, daemon=True)
        input_thread.start()
        
        while True:
            try:
                command = input_queue.get_nowait()
            except queue.Empty:
                # If no input, yield to let other tasks run
                await asyncio.sleep(0.1)
                continue
            
            match command:
                case "exit":
                    logger.inform(f"{SUCCESS}Exiting spoofing mode...{Style.RESET_ALL}")
                    run_input = False  # Signal the input thread to stop
                    break  #
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
                        mac_monitoring_active = True
                        mac_check_time = time.time()
                        while mac_monitoring_active:
                            # Check for any commands in the queue that might stop monitoring
                            try:
                                cmd = input_queue.get_nowait()
                                if cmd == "exit" or cmd == "stop":
                                    mac_monitoring_active = False
                                    logger.inform("Stopping MAC monitoring")
                            except queue.Empty:
                                # No command to stop, continue monitoring
                                pass
                                
                            # Only update MAC display every 3 seconds
                            current_time = time.time()
                            if current_time - mac_check_time >= 3:
                                logger.log("MAC: " + sys_info.mac)
                                mac_check_time = current_time
                                
                            # Yield to other tasks
                            await asyncio.sleep(0.1)
                case "backup":
                    logger.inform(f"{Fore.YELLOW}Creating registry backup...{Style.RESET_ALL}")
                    # Assuming spoofer.create_registry_backup() is an async operation
                    # If not, you might need await spoofer.create_registry_backup() if create_registry_backup is an awaitable
                    spoofer.create_registry_backup()
                    backup = True
                    logger.inform(f"{SUCCESS}Backup created successfully.{Style.RESET_ALL}")
                case "info":
                    logger.log(sys_info.get())
                case _:  # Wildcard case for any other input
                    logger.error(f"{ERROR} Unknown command: {command}{Style.RESET_ALL}")
    except asyncio.CancelledError:
        logger.inform(f"Exiting program...")
        raise
    except Exception as e:
        logger.error(f"{ERROR}Error found during spoofing:{Style.RESET_ALL}", sys.exc_info())


def cleanup_function():
    global thread
    if thread and hasattr(thread, '_listener'):
        thread._listener.stop()
    logger.save()
    config.save()
    logger.inform(f"Exited program...")

atexit.register(cleanup_function)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
