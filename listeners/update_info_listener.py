import time

from system_information import SystemInformation
from utils.logger import Logger
from colorama import Fore, Style

class UpdateInfoListener:
    def __init__(self, sys_info: SystemInformation, logger: Logger):
        self._sys_info = sys_info
        self._logger = logger
        self._oldInfo = {}
        self._running = True
        self._oldInfo = self._sys_info.getAll()
        self._keys = {}
        self._oldValues = {}
        self._paused = False
        for key in self._oldInfo.keys():
            self._keys[key] = "updated_" + key
            self._oldValues[key] = getattr(self._sys_info, f"_SystemInformation__{key}")
       

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
    
    def is_paused(self):
        return self._paused
        
    def stop(self):
        self._running = False

    def _check(self):
        newInfo = self._sys_info.getAllUpdated()
        for oldKey, newKey in self._keys.items():
            if newKey in newInfo:
                value = newInfo[newKey]
                oldValue = self._oldInfo[oldKey]
                
                # Only update and log if both values exist and are different
                if oldValue is not None and value is not None and oldValue != value:
                    setattr(self._sys_info, f"_SystemInformation__{oldKey}", value)
                    self._logger.inform(f"{Fore.YELLOW} [LISTENER] {Fore.RESET} Updated {Fore.LIGHTMAGENTA_EX}{oldKey}{Fore.RESET} from {Fore.LIGHTMAGENTA_EX}{oldValue}{Fore.RESET} to{Fore.YELLOW} {value}{Fore.RESET} from {Fore.YELLOW}{newKey}")
                    # Update old info for future comparisons
                    self._oldInfo[oldKey] = value
            else:
                self._logger.debug(f"Key {oldKey} not found in newInfo")

    def run(self):
        while self._running:
            try:
                if not self._paused:
                    self._check()
                    time.sleep(2)
            except KeyboardInterrupt:
                self._logger.inform(f"Listener exiting...")
                self._running = False
                break
