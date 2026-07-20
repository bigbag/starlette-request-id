"""Pure ASGI middleware for request-ID context propagation."""

from collections.abc import Callable
from uuid import uuid4

from request_id_helper import request_id_ctx
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .constants import REQUEST_ID_HEADER

RequestIdGenerator = Callable[[], str]


def _get_default_id() -> str:
    return str(uuid4())


class RequestIdMiddleware:
    """Expose a request ID through the shared context and response headers."""

    def __init__(
        self,
        app: ASGIApp,
        id_header: str = REQUEST_ID_HEADER,
        get_default_id_func: RequestIdGenerator = _get_default_id,
    ) -> None:
        self.app = app
        self.id_header = id_header
        self.get_default_id_func = get_default_id_func

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = Headers(scope=scope).get(self.id_header)
        if request_id is None:
            request_id = self.get_default_id_func()

        request_id_ctx.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[self.id_header] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_ctx.reset()
