import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient


@pytest.fixture()
def app():
    app_ = Starlette()

    @app_.route("/")
    def success(request):
        return PlainTextResponse("Test", status_code=200)

    return app_


@pytest.fixture
def client(app):
    return TestClient(app)
