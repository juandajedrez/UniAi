from .branch_config import DEBUG

def log(message):
    if DEBUG:
        print(f"[LOG] {message}")
    else:
        pass

def log_error(message, e:Exception):
    if DEBUG:
        print(f"[ERROR] {message}")
        print(f"-> {e}")
    else:
        pass

def log_warning(message):
    if DEBUG:
        print(f"[WARNING] {message}")   
    else:
        pass

def log_info(message):
    if DEBUG:
        print(f"[INFO] {message}")
    else:
        pass

def log_debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")
    else:
        pass

def log_success(message):
    if DEBUG:
        print(f"[SUCCESS] {message}")
    else:
        pass

def espace():
    if DEBUG:
        print("\n")
    else:
        pass

def title(message:str):
    if DEBUG:
        print(f"---------- {message} ----------")
    else:
        pass






espace()
title("Cargando modulos")
log_success("Logger.py cargado exitosamente")