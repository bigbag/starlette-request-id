from uuid import UUID
from starlette_request_id.constants import REQUEST_ID_HEADER
from starlette_request_id.middleware import request_id_ctx


def test_if_request_id_in_header(client):
    TEST_REQUEST_ID = "TEST-REQUEST-ID"
    response = client.get("/", headers={REQUEST_ID_HEADER: TEST_REQUEST_ID})
    assert response.status_code == 200

    assert REQUEST_ID_HEADER in response.headers
    assert response.headers[REQUEST_ID_HEADER] == TEST_REQUEST_ID


def test_if_request_id_not_in_header(client):
    response = client.get("/")
    assert response.status_code == 200

    assert REQUEST_ID_HEADER in response.headers
    assert UUID(response.headers[REQUEST_ID_HEADER])


def test_request_id_ctx():
    assert request_id_ctx.set("TEST") is None
    assert request_id_ctx.get() == "TEST"
