"""Serve the request-ID example with Gunicorn's Uvicorn worker."""

from examples.runner_app import create_app

app = create_app()
