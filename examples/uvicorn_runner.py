"""Run the request-ID example with Uvicorn."""

from examples.runner_app import LOGGING, create_app

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=LOGGING)
