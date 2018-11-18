import datetime
import json
from pathlib import Path
from typing import Union, Optional

from flexislack.user_api.message_type import Channel, GroupConversation, PrivateConversation, SlackInstance, Message
from flexislack.backend.slack_api import ApiWrapper


class Index:
    def __init__(self, index_path: Path):
        self._index_file_path = Path("/home/ks/a/flexible-notifications-from-slack/workspaces/default/index.json")
        self._data = None

    def __enter__(self):
        self._data = json.load(self._index_file_path.open("r"))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            json.dump(self._data, self._index_file_path.open("w"))

    @property
    def _timestamps(self):
        return self._data.setdefault('timestamps', {})

    def get(self, channel: Union[PrivateConversation, GroupConversation, Channel]) -> Optional[datetime.datetime]:
        serialized = self._timestamps.get(repr(channel), None)
        if serialized:
            return self.str_to_ts(serialized)

    def set(self, channel: Union[PrivateConversation, GroupConversation, Channel], ts: datetime.datetime) -> None:
        self._timestamps[repr(channel)] = self.ts_to_str(ts)

    datetime_format = "%Y-%m-%d_%H:%M:%S.%f_%z"

    @classmethod
    def ts_to_str(cls, ts: datetime.datetime) -> str:
        return ts.strftime(cls.datetime_format)

    @classmethod
    def str_to_ts(cls, str_datetime: str) -> datetime.datetime:
        return datetime.datetime.strptime(str_datetime, cls.datetime_format)


def get_new_messages(secret: str, index_path: Path):
    api = ApiWrapper(secret)
    slack_instance = SlackInstance("unknown")
    with Index(index_path) as index:
        for channel_obj in api.channels:
            conversation = Channel(channel_obj["name"])
            latest_ts = index.get(conversation)
            for msg_obj in api.get_messages(channel_obj["id"], index.get(conversation)):
                ts = Index.str_to_ts(msg_obj["created"])
                latest_ts = max(ts, latest_ts)
                yield Message(slack_instance=slack_instance, conversation=conversation,
                              author=api.user_map.get_username(msg_obj),
                              text=msg_obj["text"],
                              created=ts)
            index.set(conversation, latest_ts)
