import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from starlette_request_id import REQUEST_ID_HEADER, RequestIdMiddleware, init_logger, request_id_ctx

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(levelname)s [%(request_id)s] %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

init_logger(LOGGING)
logger = logging.getLogger(__name__)
app = Starlette()
app.add_middleware(RequestIdMiddleware)


async def homepage(request: Request) -> JSONResponse:
    request_id = request_id_ctx.get()
    downstream_headers = {REQUEST_ID_HEADER: request_id}
    logger.info("handling request")
    return JSONResponse({"request_id": request_id, "downstream_headers": downstream_headers})


app.add_route("/", homepage)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
