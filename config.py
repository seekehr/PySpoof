import json
import os
from threading import Lock
from typing import TypeVar, Generic
from utils.logger import Logger

V = TypeVar('V')

class Config:
    _instance = None
    _lock = Lock()  # Protect against race conditions
    _config_data = None

    def __new__(cls, logger: Logger, path='./resources/config.json'):
        with cls._lock:  # Ensure thread-safety during instance creation
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance._config_data = cls._instance._load_config(path)
                cls._instance._path = path  # Store the path of the config file
                cls._instance._logger = logger
        return cls._instance

    def __init__(self, logger: Logger, path='./resources/config.json'):
        pass

    def _load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r') as file:
            parsedData = json.load(file)
            if not isinstance(parsedData, dict): # if config is somehow corrupted and completely empty
                parsedData = {"output": "none"}
            elif not parsedData.get("output"):
                parsedData["output"] = "none"
            return parsedData

    def save(self):
        with self._lock:
            if self._config_data is None:
                raise ValueError("Config data is empty, nothing to save.")
            with open(self._path, 'w') as file:
                json.dump(self._config_data, file, indent=4)
                self._logger.success(f"Config saved to {self._path}")

    def get(self, key: str) -> V:
        return self._config_data.get(key, None)

    def has(self, key: str) -> bool:
        return key in self._config_data

    def getData(self):
        return self._config_data

    def set(self, key: str, value: V):
        with self._lock:
            if self._config_data is None:
                raise ValueError("Config data is empty, nothing to set.")
            self._config_data[key] = value

    def setNested(self, value, *keys):
        with self._lock:
            if self._config_data is None:
                raise ValueError("Config data is empty, nothing to set.")
            data = self._config_data
            for key in keys[:-1]:  # Traverse until the second-to-last key (e.g: if keys is c,a,b we traverse till b)
                if key not in data or not isinstance(data[key], dict): #
                    data[key] = {}  # Create an empty dictionary if the key doesn't exist # if b doesn't exist create it
                data = data[key]  # Move deeper into the nested dictionary
            data[keys[-1]] = value  # Set the final key's value


    def getNested(self, *keys: str, default=None):
        data = self._config_data
        result = default

        def traverse(traverseData, key_list):
            nonlocal result
            if isinstance(traverseData, dict):
                for key, value in traverseData.items():
                    if key in key_list:
                        result = value
                    traverse(value, key_list)
        traverse(data, keys)

        return result

    @property
    def database(self):
        """ Access database configuration. """
        return self._config_data.get("database", {})

    @property
    def app(self):
        """ Access app configuration. """
        return self._config_data.get("app", {})

    def __repr__(self):
        """ Custom string representation of the Config object. """
        return f"<Config debug={self.app.get('debug', False)}>"
