from abc import ABC, abstractmethod
from typing import Union

from flexislack.datatypes import Message, PrivateConversation, GroupConversation, Channel
from flexislack.notification import emit_notification


class EventHandler(ABC):
    @abstractmethod
    def handle(self, message: Message):
        pass


class SimpleEventHandler(EventHandler):
    def handle(self, message: Message):
        emit_notification("Message from slack", self.common_format(message, sep=' '))

    @classmethod
    def common_format(cls, message: Message, sep='\n'):
        return f"Message on {message.slack_instance.url}{sep}" \
               f"in {cls.desc_of_conversation(message.conversation)}{sep}" \
               f"from {message.author}{sep}" \
               f"that goes as follows:{sep}" \
               f"{message.text}"

    @staticmethod
    def desc_of_conversation(c: Union[PrivateConversation, GroupConversation, Channel]):
        if isinstance(c, PrivateConversation):
            return "private conversation"
        if isinstance(c, GroupConversation):
            return f"group conversation with members {', '.join(c.members)}"
        if isinstance(c, Channel):
            return f"channel {c.name}"
        return "unknown conversation"
