from django.conf import settings
from pathlib import Path
import sys, os

LOG_DIR = Path("..") / "logs"
DJANGO_LOG_LEVEL = "DEBUG" if settings.DEBUG else "INFO"

os.makedirs(LOG_DIR, exist_ok=True) # makes sure a logs folder exists

log_filename = LOG_DIR / "django_app.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[{levelname}] [{asctime:s}] [{name}->{module}.py (line {lineno:d})]: {message}",
            'style': '{',
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[{levelname}] [{message}]',
            'style': '{'
        },
    },
    'handlers': {
        "file": {
            'level': DJANGO_LOG_LEVEL,
            "class": "backend.logging.handlers.CustomRotatingFileHandler",
            "filename": log_filename,
            "when": "midnight",
            "backupCount": 30,
            "formatter": "verbose"
        },
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': DJANGO_LOG_LEVEL,
        }
    }
}