import uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from starlette_request_id import REQUEST_ID_HEADER, RequestIdMiddleware, init_logger, request_id_ctx

LOGGING = {
    "version": 1,
    "disable_existing_loggers": 0,
    "formatters": {
        "default": {
            "()": "request_id_helper.RequestIdFormatter",
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
        return PlainTextResponse(f"Request id: {request_id_ctx.get()}", status_code=200)

    return app_


app = init_app()

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        log_config=LOGGING,
    )
