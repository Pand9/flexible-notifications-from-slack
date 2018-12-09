import datetime
import json
from pathlib import Path
from typing import Optional

import dateutil.parser

from slack_notifications.user_api.message_type import Conversation
from pid import PidFile


class Index:
    """
    There's a file on disc called "local state file" and it says when was the last timestamp pulled from Slack.
    """
    def __init__(self, index_path: Path):
        self._index_path = index_path
        self._data = None
        self._pidfile = PidFile("index", piddir="/tmp", lock_pidfile=True)

    def __enter__(self):
        if self._data is not None:
            raise Exception("can only enter once")
        self._index_path.parent.mkdir(exist_ok=True, parents=True)
        self._pidfile.create()
        if not self._index_path.exists():
            self._index_path.write_text("{}")
        self._data = json.load(self._index_path.open("r"))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            json.dump(self._data, self._index_path.open("w"), indent=4)
        self._pidfile.close()
        self._data = None

    def ts(self, channel: Conversation) -> Optional[datetime.datetime]:
        serialized = self._timestamps.get(repr(channel))
        if serialized:
            return self._str_to_ts(serialized)

    def set_ts(self, channel: Conversation, ts: datetime.datetime) -> None:
        self._timestamps[repr(channel)] = self._ts_to_str(ts)

    def set_all(self, ts):
        for k in self._timestamps:
            self._timestamps[k] = self._ts_to_str(ts)

    @classmethod
    def _ts_to_str(cls, ts: datetime.datetime) -> str:
        return ts.strftime(cls.datetime_format)

    @classmethod
    def _str_to_ts(cls, str_datetime: str) -> datetime.datetime:
        return datetime.datetime.strptime(str_datetime, cls.datetime_format)

    @property
    def _timestamps(self):
        return self._data.setdefault('timestamps', {})

    datetime_format = "%Y-%m-%d_%H:%M:%S.%f_%z"
