import datetime
from dataclasses import dataclass
from typing import Union, List


@dataclass
class SlackInstance:
    name: str

    @property
    def url(self):
        return f"{self.name}.slack.com"

@dataclass
class PrivateConversation:
    member: str

@dataclass
class Channel:
    name: str

@dataclass
class GroupConversation:
    members: List[str]

Conversation = Union[PrivateConversation, GroupConversation, Channel]

@dataclass
class Message:
    slack_instance: SlackInstance
    conversation: Conversation
    author: str
    text: str
    created: datetime.datetime
