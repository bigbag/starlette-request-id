"""Gunicorn configuration for ``examples.gunicorn_runner:app``."""

from request_id_helper import RequestIdFormatter

workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
loglevel = "info"
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": RequestIdFormatter,
            "format": "%(levelname)s [%(request_id)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "gunicorn.error": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "gunicorn.access": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
