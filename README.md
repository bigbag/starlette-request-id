# starlette-request-id

[![CI](https://github.com/bigbag/starlette-request-id/workflows/CI/badge.svg)](https://github.com/bigbag/starlette-request-id/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/bigbag/starlette-request-id/branch/main/graph/badge.svg?token=ZRUN7SUKB2)](https://codecov.io/gh/bigbag/starlette-request-id)
[![pypi](https://img.shields.io/pypi/v/starlette-request-id.svg)](https://pypi.python.org/pypi/starlette-request-id)
[![downloads](https://img.shields.io/pypi/dm/starlette-request-id.svg)](https://pypistats.org/packages/starlette-request-id)
[![versions](https://img.shields.io/pypi/pyversions/starlette-request-id.svg)](https://github.com/bigbag/starlette-request-id)
[![license](https://img.shields.io/github/license/bigbag/starlette-request-id.svg)](https://github.com/bigbag/starlette-request-id/blob/master/LICENSE)


**starlette-request-id** is a helper for starlette to add request id in logger.

* [Project Changelog](https://github.com/bigbag/starlette-request-id/blob/main/CHANGELOG.md)

## Installation

starlette-request-id is available on PyPI.
Use pip to install:

    $ pip install starlette-request-id

## Basic Usage

```py
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette_request_id import REQUEST_ID_HEADER, RequestIdMiddleware, init_logger, request_id_ctx

LOGGING = {
    "version": 1,
    "disable_existing_loggers": 0,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s [%(request_id)s] %(name)s | %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        }
    },
    "handlers": {
        "stdout": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["stdout"],
            "propagate": True,
            "level": "INFO",
        },
    },
}


def init_app():
    init_logger(LOGGING)

    app_ = Starlette()
    app_.add_middleware(RequestIdMiddleware)

    @app_.route("/")
    def success(request):
        httpx.post("https://www.example.org/", headers={REQUEST_ID_HEADER: request_id_ctx.get()})
        return PlainTextResponse("OK", status_code=200)

    return app_


app = init_app()

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        log_config=LOGGING,
    )

```

curl 127.0.0.1:8000

```bash
    [17/Jan/2021 18:31:19] INFO [N/A] uvicorn.error | Started server process [576540]
    [17/Jan/2021 18:31:19] INFO [N/A] uvicorn.error | Waiting for application startup.
    [17/Jan/2021 18:31:19] INFO [N/A] uvicorn.error | Application startup complete.
    [17/Jan/2021 18:31:19] INFO [N/A] uvicorn.error | Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    [17/Jan/2021 18:31:22] INFO [22395fa2-e296-420e-93a1-5537e1ba0a62] uvicorn.access | 127.0.0.1:50372 - "GET / HTTP/1.1" 200
    [17/Jan/2021 18:31:25] INFO [9ac6fa25-5048-4222-ac54-dd2c70e3e042] uvicorn.access | 127.0.0.1:50374 - "GET / HTTP/1.1" 200
```
## License

starlette-request-id is developed and distributed under the Apache 2.0 license.

## Reporting a Security Vulnerability

See our [security policy](https://github.com/bigbag/starlette-request-id/security/policy).
