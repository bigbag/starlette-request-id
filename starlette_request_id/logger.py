from logging import LogRecord, setLogRecordFactory
from logging.config import dictConfig
from typing import Any, Dict

from . import helper


class LogExtraFactory(LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_id = helper.request_id_ctx.get() or "N/A"

        self.__dict__["request_id"] = request_id


def init_logger(config: Dict[str, Any]):
    dictConfig(config)
    setLogRecordFactory(LogExtraFactory)
