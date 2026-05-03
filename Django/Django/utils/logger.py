from .branch_config import DEBUG

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
COLOR_CLOSE = "\033[0m"
MAGENTA = "\033[35m"
CIAN = "\033[36m"

def log(message):
    if DEBUG:
        print(f"{CIAN}[LOG] {message}{COLOR_CLOSE}")
    else:
        pass

def log_error(message, e:Exception):
    if DEBUG:
        print(f"{RED}[ERROR] {message}{COLOR_CLOSE}")
        print(f"-> {e}")
    else:
        pass

def log_warning(message):
    if DEBUG:
        print(f"{YELLOW}[WARNING] {message}{COLOR_CLOSE}")   
    else:
        pass

def log_info(message):
    if DEBUG:
        print(f"{BLUE}[INFO] {message}{COLOR_CLOSE}")
    else:
        pass

def log_debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")
    else:
        pass

def log_success(message):
    if DEBUG:
        print(f"{GREEN}[SUCCESS] {message}{COLOR_CLOSE}")
    else:
        pass

def espace():
    if DEBUG:
        print("\n")
    else:
        pass

def title(message:str):
    if DEBUG:
        print(f"{MAGENTA}---------- {message} ----------{COLOR_CLOSE}")
    else:
        pass




espace()
title("Cargando modulos")
log_success("branch_config.py cargado exitosamente")
log_success("Logger.py cargado exitosamente")