def log(message):
    print(f"[LOG] {message}")

def log_error(message, e:Exception):
    print(f"[ERROR] {message}")
    print(f"-> {e}")

def log_warning(message):
    print(f"[WARNING] {message}")   

def log_info(message):
    print(f"[INFO] {message}")

def log_debug(message):
    print(f"[DEBUG] {message}")

def log_success(message):
    print(f"[SUCCESS] {message}")

def espace():
    print("\n")

def title(message:str):
    print(f"---------- {message} ----------")






espace()
title("Cargando modulos")
log_success("Logger.py cargado exitosamente")