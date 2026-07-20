"""Shared Starlette application for the Uvicorn and Gunicorn examples."""

import logging
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from starlette_request_id import RequestIdMiddleware, init_logger, request_id_ctx

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s [%(request_id)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


def create_app() -> Starlette:
    """Create an application that returns and logs the active request ID."""
    init_logger(LOGGING)
    app = Starlette()
    app.add_middleware(RequestIdMiddleware)

    async def homepage(request: Request) -> PlainTextResponse:
        request_id = request_id_ctx.get()
        logging.getLogger(__name__).info("handling request")
        return PlainTextResponse(f"Request ID: {request_id}")

    app.add_route("/", homepage)
    return app
