import inspect
import threading
from types import TracebackType
from typing import Type

from utils.formats import *

"""
Thread safe logger
"""
class Logger:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls, path, debug=False):
        # Use the class-level lock to ensure thread-safe instance creation
        with cls._lock:
            if cls._instance is None:
                # Create the instance using the parent class's __new__ method
                cls._instance = super(Logger, cls).__new__(cls)
                # Initialize the instance (this is typically done in __init__)
                # We call this here because __init__ won't be called on subsequent calls to Logger()
                cls._instance._path = path
                cls._instance._logs = []
                cls._instance._debug = debug
                cls._instance._log_lock = threading.Lock()
                cls._instance._save_lock = threading.Lock()
        return cls._instance

    def __init__(self, path, debug=False):
        self._debug = False

    def setDebug(self, debug: bool):
        self._debug = debug

    def log(self, message: str):
        with self._lock:
            self._logs.append(message + "\n")
        print(message) # Printing is generally thread-safe for standard output

    def inform(self, message: str):
        with self._lock:
            self._logs.append(" " + message + "\n")
        print(INFO + message)

    import traceback

    def warn(self, message: str,
             err: tuple[Type[BaseException], BaseException, TracebackType] | tuple[None, None, None] | None = None):
        log_message = message
        if err is not None:
            log_message = " " + message
            exc_type, exc_obj, tb = err

            # Extract details from the traceback object
            line_number = tb.tb_lineno
            file_name = tb.tb_frame.f_code.co_filename

            # The exception is in exc_obj, and it's already an instance of Exception (or its subclass)
            if isinstance(exc_obj, Exception):
                log_message += f".. Exception: {str(exc_obj)} at line {line_number} in {file_name}"

        string = " " + message
        if err:
            # Use exc_obj to format the error string instead of the whole tuple
            exc_type, exc_obj, tb = err
            string += f". Exception: {str(exc_obj)}"

        # Assuming you have a lock and a log list for thread-safety
        with self._lock:
            self._logs.append(string + "\n")

        # Print the log message
        print(WARNING + log_message)

    def error(self, message: str,
              err: tuple[Type[BaseException], BaseException, TracebackType] | tuple[None, None, None] | None = None):
        log_message = " "
        if err is not None:
            log_message = message
            exc_type, exc_obj, tb = err

            # Extract details from the traceback object
            line_number = tb.tb_lineno
            file_name = tb.tb_frame.f_code.co_filename

            # The exception is in exc_obj, and it's already an instance of Exception (or its subclass)
            if isinstance(exc_obj, Exception):
                log_message += f".. Exception: {str(exc_obj)} at line {line_number} in {file_name}"
                print("Exception details captured")

        else:
            log_message = " " + message

        # Assuming you have a lock and a log list for thread-safety
        with self._lock:
            self._logs.append(log_message + "\n")

        # Print the log message
        print(ERROR + log_message)

    def success(self, message: str):
        with self._lock:
            self._logs.append(" " + message + "\n")
        print(SUCCESS + message)

    def debug(self, message: str):
        if not self._debug: return
        with self._lock:
            self._logs.append(" " + message + "\n")
        print(DEBUG + message)
        
    def save(self):
        with self._save_lock:
            try:
                with open(self._path, 'w') as file:
                    for log in self._logs:
                        file.write(parse_raw_text(log) + '\n')
                self.success(f"Logger file saved to {self._path}.")
            except IOError as e:
                print(f"ERROR: Failed to save log file {self._path}: {e}")
