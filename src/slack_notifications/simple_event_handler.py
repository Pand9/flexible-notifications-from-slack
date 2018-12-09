from typing import Union, List

from slack_notifications.user_api.emit_ubuntu_notification import emit_notification
from slack_notifications.user_api.event_handler_interface import EventHandler
from slack_notifications.user_api.message_type import Message, PrivateConversation, GroupConversation, Channel, Conversation

class SimpleEventHandler(EventHandler):
    def handle(self, conversation: Conversation, messages: List[Message]):
        if not isinstance(conversation, Channel) or any("<@U971CT4Q1>" in m.text for m in messages):
            emit_notification("%d messages on %s" % (len(messages), conversation), self.common_format(messages[-1]))

    @staticmethod
    def limit_line(line, limit):
        if len(line) <= limit:
            return line
        return f"{line[:limit - 6]} [...]"

    @classmethod
    def common_format(cls, message: Message):
        return f"Message on '{message.slack_instance.url}' " \
               f"in '{cls.limit_line(cls.desc_of_conversation(message.conversation), 50)}' " \
               f"from '{message.author}' " \
               f"that goes as follows:\n" \
               f"{cls.limit_line(message.text, 80)}"

    @staticmethod
    def desc_of_conversation(c: Union[PrivateConversation, GroupConversation, Channel]):
        if isinstance(c, PrivateConversation):
            return "private conversation"
        if isinstance(c, GroupConversation):
            return f"group conversation with members {', '.join(c.members)}"
        if isinstance(c, Channel):
            return f"channel {c.name}"
        return "unknown conversation"
