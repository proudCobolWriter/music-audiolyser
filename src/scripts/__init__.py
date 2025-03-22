#!/usr/bin/env python
import sys, os

def setSettings() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

def importExecuteCLI() -> callable:
    try:
        from django.core.management import execute_from_command_line
        return execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

# General admin

def django_manage() -> None:
    setSettings()
    importExecuteCLI()(sys.argv)

# Some shortcuts

def run_django() -> None:
    setSettings()
    importExecuteCLI()([sys.argv[0], "runserver", *sys.argv[1:]])
    
def collect_static_django() -> None:
    setSettings()
    importExecuteCLI()([sys.argv[0], "collectstatic", "--noinput", *sys.argv[1:]])