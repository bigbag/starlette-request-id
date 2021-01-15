import typing as t
import uuid
from dataclasses import dataclass, field

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from . import constants, context


def _get_default_id() -> str:
    return str(uuid.uuid4())


class RequestIdCtx(context.ContextStorage):
    CONTEXT_KEY_NAME = "request_id"


request_id_ctx = RequestIdCtx()


@dataclass
class RequestIdMiddleware(BaseHTTPMiddleware):
    app: ASGIApp
    id_header: str = constants.REQUEST_ID_HEADER
    get_default_id_func: t.Callable = _get_default_id
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(self.id_header, self.get_default_id_func())

        request_id_ctx.set(request_id)
        response = await call_next(request)
        response.headers[self.id_header] = request_id
        return response
