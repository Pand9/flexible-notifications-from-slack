import datetime
from functools import lru_cache
from typing import List, Callable, Optional, Iterable, Tuple

import pytz as pytz
import slackclient

from slack_notifications.user_api.message_type import Channel, Conversation, Message, PrivateConversation, GroupConversation, \
    SlackInstance


class UserMap:
    def __init__(self, user_id_to_name):
        self._user_id_to_name = user_id_to_name

    def get_username(self, raw: dict):
        if "user" in raw:
            return self._user_id_to_name[raw["user"]]
        if "bot_id" in raw:
            return raw["bot_id"]
        if "id" in raw:
            return raw["id"]
        raise Exception("unknown username: %s" % raw)

    def from_id(self, user_id: str):
        return self._user_id_to_name[user_id]

    @classmethod
    def from_api_wrapper(cls, api_wrapper):
        users = api_wrapper.get_users_list()
        return cls({u["id"]: u["name"] for u in users["members"]})

def parse_ts(tsarg):
    ts, msec = map(int, tsarg.split("."))
    return datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.UTC, microsecond=msec)

def deparse_ts(dt: datetime.datetime):
    return "{}.{}".format(dt.timestamp(), dt.microsecond)

class ApiWrapper:
    def _channel(self, raw):
        return Channel(name=raw["name"])

    def _private_conversation(self, raw):
        return PrivateConversation(member=self.user_map.get_username(raw))

    def _group_conversation(self, raw):
        return GroupConversation(members=[self.user_map.from_id(raw_user_id) for raw_user_id in raw["members"]])

    def _message(self, raw: dict, conversation: Conversation):
        try:
            return Message(slack_instance=self.slack, conversation=conversation, author=self.user_map.get_username(raw),
                           text=raw["text"], created=parse_ts(raw["ts"]))
        except:
            print(raw)
            raise

    def __init__(self, secret, slack: SlackInstance):
        self.slack = slack
        self._slackclient = slackclient.SlackClient(secret)

    def api_call(self, *a, **kw):
        print("api call: %s, %s" % (a, kw))
        resp = self._slackclient.api_call(*a, **kw)
        if not resp["ok"]:
            raise Exception("not ok: %s" % resp)
        return resp

    def _conversation_messages(self,
                               conv: Conversation,
                               conv_id: str,
                               first_ts_provider: Callable[[Conversation], Optional[datetime.datetime]],
                               api_call_name: str):
        first_ts = first_ts_provider(conv) or datetime.datetime(1980, 1, 1)
        resp = self.api_call(api_call_name, channel=conv_id, count=100, oldest=deparse_ts(first_ts))
        if not resp.get("messages"):
            return
        return [self._message(raw, conv) for raw in resp["messages"]]

    def messages(self, first_ts_provider: Callable[[Conversation], Optional[datetime.datetime]]) -> List[Tuple[Conversation, List[Message]]]:
        result = []
        for channel_raw in self.channel_raws:
            channel = self._channel(channel_raw)
            messages = self._conversation_messages(channel, channel_raw["id"], first_ts_provider, "channels.history")
            if messages:
                result.append((channel, messages))
        for group_conv_raw in self.group_conversation_raws:
            group_conv = self._group_conversation(group_conv_raw)
            messages = self._conversation_messages(group_conv, group_conv_raw["id"], first_ts_provider, "groups.history")
            if messages:
                result.append((group_conv, messages))
        for private_conv_raw in self.private_conversation_raws:
            private_conv = self._private_conversation(private_conv_raw)
            messages = self._conversation_messages(private_conv, private_conv_raw["id"], first_ts_provider, "im.history")
            if messages:
                result.append((private_conv, messages))
        return result

    @property
    @lru_cache()
    def channel_raws(self) -> List[dict]:
        return list(self.api_call("channels.list")["channels"])

    @property
    @lru_cache()
    def group_conversation_raws(self) -> List[dict]:
        return list(self.api_call("groups.list")["groups"])

    @property
    @lru_cache()
    def private_conversation_raws(self) -> List[dict]:
        return list(self.api_call("im.list")["ims"])

    @property
    @lru_cache()
    def users(self):
        return self.api_call("users.list")["members"]

    @property
    @lru_cache()
    def user_map(self) -> UserMap:
        return UserMap({u["id"]: u["name"] for u in self.users})

if __name__ == "__main__":
    a = ApiWrapper(secret, SlackInstance("stratslab"))

