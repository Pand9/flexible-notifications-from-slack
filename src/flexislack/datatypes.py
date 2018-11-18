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

@dataclass
class Message:
    slack_instance: SlackInstance
    conversation: Union[PrivateConversation, GroupConversation, Channel]
    author: str
    text: str
    created: datetime.datetime
