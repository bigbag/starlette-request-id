from . import context


class RequestIdCtx(context.ContextStorage):
    CONTEXT_KEY_NAME = "request_id"


request_id_ctx = RequestIdCtx()
