import re

from colorama import Fore, Back, Style
SUCCESS = Fore.GREEN + "[SUCCESS] " + Style.RESET_ALL
WARNING = Fore.YELLOW + "[WARNING] " + Style.RESET_ALL
ERROR = Fore.RED + "[ERROR] " + Style.RESET_ALL
INFO = Fore.BLUE + "[INFO] " + Style.RESET_ALL
DEBUG = Style.DIM + "[DEBUG] " + Style.RESET_ALL

def parse_raw_text(text: str):
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape_pattern.sub('', text)