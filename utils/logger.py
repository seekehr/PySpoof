import inspect

from utils.formats import *
class Logger:
    def __init__(self, path):
        self._path = path
        self._logs = []

    def log(self, message: str):
        self._logs.append(message)
        print(message)

    def inform(self, message: str):
        self._logs.append(INFO + message)
        print("[INFO]: " + message)

    def warn(self, message: str, err: Exception = None):
        self._logs.append("[WARNING]: " + message + f".. Exception:" + str(err))
        print(WARNING + message + f"... {Fore.RESET} Exception:" + str(err))

    def error(self, message: str, err: Exception = None):
        self._logs.append("[ERROR]: " + message + f".. Exception:" + str(err))
        print(ERROR + message + f"... {Fore.RESET} Exception:" + str(err))

    def success(self, message: str):
        self._logs.append("[SUCCESS]: " + message)
        print(SUCCESS + message)

    def save(self):
        with open(self._path, 'w') as file:
            for log in self._logs:
                file.write(log + '\n')