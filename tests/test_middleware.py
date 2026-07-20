import asyncio
from collections.abc import Callable
from uuid import UUID

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.testclient import TestClient
from starlette.types import ASGIApp, Message, Scope

from starlette_request_id import REQUEST_ID_HEADER, RequestIdMiddleware, request_id_ctx


def create_client(
    *,
    id_header: str = REQUEST_ID_HEADER,
    get_default_id_func: Callable[[], str] | None = None,
) -> TestClient:
    app = Starlette()
    app.add_middleware(
        RequestIdMiddleware,
        id_header=id_header,
        **({"get_default_id_func": get_default_id_func} if get_default_id_func else {}),
    )

    async def homepage(request: Request) -> JSONResponse:
        return JSONResponse({"request_id": request_id_ctx.get()}, headers={id_header: "stale"})

    app.add_route("/", homepage)
    return TestClient(app)


def test_supplied_request_id_is_available_to_the_application_and_response() -> None:
    with create_client() as client:
        response = client.get("/", headers={REQUEST_ID_HEADER: "client-id"})

    assert response.status_code == 200
    assert response.json() == {"request_id": "client-id"}
    assert response.headers[REQUEST_ID_HEADER] == "client-id"


def test_missing_request_id_uses_a_uuid4_value() -> None:
    with create_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["request_id"] == response.headers[REQUEST_ID_HEADER]
    assert UUID(response.headers[REQUEST_ID_HEADER]).version == 4


def test_default_generator_is_not_called_when_the_client_supplies_an_id() -> None:
    calls: list[str] = []

    def generate_id() -> str:
        calls.append("called")
        return "generated-id"

    with create_client(get_default_id_func=generate_id) as client:
        response = client.get("/", headers={REQUEST_ID_HEADER: "client-id"})

    assert response.headers[REQUEST_ID_HEADER] == "client-id"
    assert calls == []


def test_empty_supplied_request_id_is_preserved() -> None:
    with create_client(get_default_id_func=lambda: "generated-id") as client:
        response = client.get("/", headers={REQUEST_ID_HEADER: ""})

    assert response.json() == {"request_id": ""}
    assert response.headers[REQUEST_ID_HEADER] == ""


def test_custom_header_and_generator_are_used() -> None:
    with create_client(
        id_header="x-correlation-id", get_default_id_func=lambda: "generated-id"
    ) as client:
        response = client.get("/")

    assert response.json() == {"request_id": "generated-id"}
    assert response.headers["x-correlation-id"] == "generated-id"


def test_middleware_replaces_an_application_request_id_response_header() -> None:
    with create_client() as client:
        response = client.get("/", headers={REQUEST_ID_HEADER: "client-id"})

    assert response.headers.get_list(REQUEST_ID_HEADER) == ["client-id"]


async def invoke_asgi(app: ASGIApp, scope: Scope) -> list[Message]:
    sent: list[Message] = []

    async def receive() -> Message:
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


def test_context_is_reset_after_a_successful_request() -> None:
    async def application(scope: Scope, receive, send) -> None:
        assert request_id_ctx.get() == "client-id"
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def run() -> None:
        middleware = RequestIdMiddleware(application)
        scope: Scope = {"type": "http", "headers": [(b"x-request-id", b"client-id")]}
        await invoke_asgi(middleware, scope)
        assert request_id_ctx.get() == ""

    asyncio.run(run())


def test_context_is_reset_after_an_application_exception() -> None:
    async def failing_app(scope: Scope, receive, send) -> None:
        assert request_id_ctx.get() == "client-id"
        raise RuntimeError("boom")

    async def run() -> None:
        middleware = RequestIdMiddleware(failing_app)
        scope: Scope = {"type": "http", "headers": [(b"x-request-id", b"client-id")]}
        with pytest.raises(RuntimeError, match="boom"):
            await invoke_asgi(middleware, scope)
        assert request_id_ctx.get() == ""

    asyncio.run(run())


def test_context_is_reset_when_a_request_is_cancelled() -> None:
    async def cancelled_app(scope: Scope, receive, send) -> None:
        assert request_id_ctx.get() == "client-id"
        raise asyncio.CancelledError()

    async def run() -> None:
        middleware = RequestIdMiddleware(cancelled_app)
        scope: Scope = {"type": "http", "headers": [(b"x-request-id", b"client-id")]}
        with pytest.raises(asyncio.CancelledError):
            await invoke_asgi(middleware, scope)
        assert request_id_ctx.get() == ""

    asyncio.run(run())


def test_non_http_scope_passes_through_without_changing_context() -> None:
    seen_scopes: list[str] = []

    async def application(scope: Scope, receive, send) -> None:
        seen_scopes.append(scope["type"])
        await send({"type": "lifespan.startup.complete"})

    scope: Scope = {"type": "lifespan"}
    sent = asyncio.run(invoke_asgi(RequestIdMiddleware(application), scope))

    assert seen_scopes == ["lifespan"]
    assert sent == [{"type": "lifespan.startup.complete"}]
    assert request_id_ctx.get() == ""


def test_concurrent_requests_keep_their_context_values_isolated() -> None:
    seen_ids: list[str] = []

    async def run_requests() -> None:
        ready = asyncio.Event()

        async def application(scope: Scope, receive, send) -> None:
            seen_ids.append(request_id_ctx.get())
            if len(seen_ids) == 2:
                ready.set()
            await ready.wait()
            assert request_id_ctx.get() in {"first", "second"}
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        middleware = RequestIdMiddleware(application)
        await asyncio.gather(
            invoke_asgi(middleware, {"type": "http", "headers": [(b"x-request-id", b"first")]}),
            invoke_asgi(middleware, {"type": "http", "headers": [(b"x-request-id", b"second")]}),
        )

    asyncio.run(run_requests())

    assert set(seen_ids) == {"first", "second"}
    assert request_id_ctx.get() == ""


def test_handled_error_response_includes_the_request_id() -> None:
    async def error_handler(request: Request, exc: Exception) -> PlainTextResponse:
        return PlainTextResponse("bad request", status_code=400)

    app = Starlette(exception_handlers={ValueError: error_handler})
    app.add_middleware(RequestIdMiddleware)

    async def endpoint(request: Request) -> PlainTextResponse:
        raise ValueError("bad request")

    app.add_route("/", endpoint)

    with TestClient(app) as client:
        response = client.get("/", headers={REQUEST_ID_HEADER: "client-id"})

    assert response.status_code == 400
    assert response.headers[REQUEST_ID_HEADER] == "client-id"
