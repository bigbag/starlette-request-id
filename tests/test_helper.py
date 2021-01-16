from starlette_request_id import request_id_ctx


def test_request_id_ctx():
    assert request_id_ctx.set("TEST") is None
    assert request_id_ctx.get() == "TEST"
