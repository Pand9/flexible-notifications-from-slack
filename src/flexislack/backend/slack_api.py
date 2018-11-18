import datetime
from functools import lru_cache

import slackclient


class UserMap:
    def __init__(self, user_id_to_name):
        self._user_id_to_name = user_id_to_name

    def get_username(self, message):
        if message.get("user"):
            return self._user_id_to_name[message["user"]]
        if message.get("bot_id"):
            return message["bot_id"]
        raise Exception("unknown username: %s" % message)

    @classmethod
    def from_api_wrapper(cls, api_wrapper):
        users = api_wrapper.get_users_list()
        return cls({u["id"]: u["name"] for u in users["members"]})


class ApiWrapper:
    def __init__(self, secret):
        self._slackclient = slackclient.SlackClient(secret
                                                    )

    def api_call(self, *a, **kw):
        resp = self._slackclient.api_call(*a, **kw)
        if not resp["ok"]:
            raise Exception("not ok")
        return resp

    def get_messages(self, channel_id: str, from_ts: datetime.datetime):
        return []

    @property
    @lru_cache
    def channels(self):
        pass

    @property
    @lru_cache
    def channel_id_to_name(self):
        pass

    @property
    @lru_cache
    def channel_name_to_id(self):
        pass

    @property
    @lru_cache
    def users(self):
        return None

    @property
    @lru_cache
    def user_map(self) -> UserMap:
        return UserMap({u["id"]: u["name"] for u in self.users["members"]})