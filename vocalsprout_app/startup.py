import os
import sys
import winreg


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "VOCALSPROUT"
# Startup entry created by AYLO (the name before VOCALSPROUT). It points at the
# old executable, so it is removed whenever the startup setting is changed.
LEGACY_VALUE_NAME = "Aylo"


def launch_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    return f'"{sys.executable}" "{main_path}"'


def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
        return value == launch_command()
    except FileNotFoundError:
        return False


def _remove_value(name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def set_startup_enabled(enabled):
    if enabled:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, launch_command())
        _remove_value(LEGACY_VALUE_NAME)
        return
    _remove_value(VALUE_NAME)
    _remove_value(LEGACY_VALUE_NAME)
