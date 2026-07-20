# starlette-request-id

Request-ID context and response propagation middleware for Starlette applications.

## Requirements

- Python 3.11+ (CI validates 3.11, 3.12, 3.13, and 3.14)
- Starlette >1.2.0 and <2.0.0

## Install

```console
uv add starlette-request-id
pip install starlette-request-id
```

## Basic usage

```python
from starlette.applications import Starlette

from starlette_request_id import RequestIdMiddleware

app = Starlette()
app.add_middleware(RequestIdMiddleware)
```

`RequestIdMiddleware` reads `x-request-id`, creates a UUID4 ID if it is absent,
exposes it through `request_id_ctx`, and writes the active value to the response
header. See `examples/basic_usage.py` for logging and outbound-header
propagation.

## Examples

Run the standalone example:

```console
uv run --with uvicorn examples/basic_usage.py
```

Run the dedicated Uvicorn example:

```console
uv run --with 'uvicorn[standard]' uvicorn examples.uvicorn_runner:app --reload
```

Run the Gunicorn example with Uvicorn workers:

```console
uv run --with gunicorn --with uvicorn gunicorn -c examples/gunicorn_conf.py examples.gunicorn_runner:app
```

Then send a request with a chosen ID:

```console
curl -H 'x-request-id: example-id' http://127.0.0.1:8000/
```

Starlette 1.3 uses `app.add_route(path, endpoint)` to register handlers; the
examples follow that API.

## Configuration

```python
app.add_middleware(
    RequestIdMiddleware,
    id_header="x-correlation-id",
    get_default_id_func=lambda: "generated-id",
)
```

A supplied value is preserved exactly; the generator is called only when the
header is absent.

## Logging

```python
from starlette_request_id import init_logger, request_id_ctx
```

These exports are the shared APIs from `request-id-helper`, so applications
that import `request_id_ctx` directly from `request_id_helper` observe the same
request value.

## Error responses and middleware order

The middleware adds the header to response starts emitted by the application
and its inner exception handlers. It does not render exceptions. If an outer
error middleware constructs a response after an exception escapes
`RequestIdMiddleware`, put that error middleware inside `RequestIdMiddleware`
or make it write the request-ID header itself.

## Migrating from 1.x

2.0.0 drops Python 3.8–3.10 and replaces the internal `BaseHTTPMiddleware`
implementation with pure ASGI middleware. Existing imports of
`RequestIdMiddleware`, `REQUEST_ID_HEADER`, `request_id_ctx`, `init_logger`,
and `LogExtraFactory` continue to work. Update deployment environments to
Python 3.11+, use Starlette's `add_route()` API, and retain `request-id-helper`
as the shared logging/context provider.

## Development

```console
uv sync --all-groups
make lint
make test
make build
```

## License

starlette-request-id is distributed under the Apache License 2.0.
