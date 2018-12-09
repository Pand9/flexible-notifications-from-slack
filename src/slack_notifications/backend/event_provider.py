from datetime import timedelta
from typing import List, Tuple

from slack_notifications.backend.index import Index
from slack_notifications.backend.slack_api import ApiWrapper
from slack_notifications.user_api.message_type import Message, Conversation


class EventProvider:
    def __init__(self, api_wrapper: ApiWrapper, local_state: Index):
        self._api = api_wrapper
        self._state = local_state

    def get_new_messages(self) -> List[Tuple[Conversation, List[Message]]]:
        new_messages = []
        for conversation, messages in self._api.messages(self._state.ts):
            messages.sort(key=lambda m: m.created)
            self._state.set_ts(conversation, messages[-1].created + timedelta(microseconds=1))
            new_messages.append((conversation, messages))
        return new_messages

