import asyncio
import uuid
from functools import wraps

from . import context


def get_default_id() -> str:
    return str(uuid.uuid4())


class RequestIdCtx(context.ContextStorage):
    CONTEXT_KEY_NAME = "request_id"


request_id_ctx = RequestIdCtx()


def set_request_id(fn):
    if asyncio.iscoroutinefunction(fn):

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            request_id_ctx.set(get_default_id())
            return await fn(*args, **kwargs)

        return wrapper
    else:

        @wraps(fn)
        def wrapper(*args, **kwargs):
            request_id_ctx.set(get_default_id())
            return fn(*args, **kwargs)

        return wrapper
