from abc import ABC, abstractmethod
from typing import List

from slack_notifications.user_api.message_type import Message, Conversation


class EventHandler(ABC):
    @abstractmethod
    def handle(self, conversation: Conversation, messages: List[Message]):
        pass
