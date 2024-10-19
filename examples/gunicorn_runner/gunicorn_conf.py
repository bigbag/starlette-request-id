import logging

from request_id_helper import RequestIdFormatter

# Gunicorn config
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "info"
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": RequestIdFormatter,
            "format": "[%(asctime)s] %(levelname)s [%(request_id)s] %(name)s | %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
