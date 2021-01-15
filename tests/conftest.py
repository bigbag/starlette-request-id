import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_request_id.middleware import RequestIdMiddleware


@pytest.fixture()
def app():
    app_ = Starlette()
    app_.add_middleware(RequestIdMiddleware)

    @app_.route("/")
    def success(request):
        return PlainTextResponse("OK", status_code=200)

    return app_


@pytest.fixture
def client(app):
    return TestClient(app)
