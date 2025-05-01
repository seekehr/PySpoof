import time

from system_information import SystemInformation
from utils.logger import Logger


class UpdateInfoListener:
    def __init__(self, sys_info: SystemInformation, logger: Logger):
        self._sys_info = sys_info
        self._logger = logger
        self._oldInfo = {}
        self._running = True

        self._keys = {}
        self._oldValues = {}
       
    def init(self):
        self._oldInfo = self._sys_info.getAll()
        for key in self._oldInfo.keys():
            self._keys[key] = "updated_" + key
            self._oldValues[key] = getattr(self._sys_info, f"_SystemInformation__{key}")

            print(self._oldValues)

    def stop(self):
        self._running = False

    def _check(self):
        newInfo = self._sys_info.getAllUpdated()
        for oldKey, newKey in self._keys.items():
            if newKey in newInfo:
                value = newInfo[newKey]
                oldValue = self._oldInfo[oldKey]
                if not oldValue: return # to prevent spam at start
                if oldValue != value:
                    setattr(self._sys_info, f"_SystemInformation__{oldKey}", value)
                    self._logger.inform(f"Updated {oldKey} from {oldValue} to {value}")
            else:
                self._logger.debug(f"Key {oldKey} not found in newInfo")
        self._logger.debug("Running listener...")

    def run(self):
        while self._running:
            try:
                self._check()
                time.sleep(2)
            except KeyboardInterrupt:
                self._logger.inform(f"Listener exiting...")
                self._running = False
                break
