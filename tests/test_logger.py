import logging

from starlette_request_id import LogExtraFactory, init_logger, request_id_ctx


class MockLogHandler(logging.Handler):
    records = []

    def emit(self, record):
        self.records.append(f"[{record.request_id}] {record.message}")


def test_log_extra_factory(caplog):
    REQUEST_ID = "REQUEST_ID"
    mock_logger = MockLogHandler()
    logger = logging.getLogger()
    logging.setLogRecordFactory(LogExtraFactory)
    logger.addHandler(mock_logger)

    request_id_ctx.set(REQUEST_ID)
    logger.error("an error")

    request_id_ctx.set(None)
    logger.error("an error")

    assert REQUEST_ID in mock_logger.records[0]
    assert "N/A" in mock_logger.records[1]

    request_id_ctx.reset()


def test_init_logger():
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": 0,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s [%(request_id)s] %(name)s | %(message)s",
                "datefmt": "%d/%b/%Y %H:%M:%S",
            }
        },
        "handlers": {
            "stdout": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "": {
                "handlers": ["stdout"],
                "propagate": True,
                "level": "INFO",
            },
        },
    }
    init_logger(LOGGING)
    logger = logging.getLogger()
    assert len(logger.handlers) == 1
