from abc import ABC, abstractmethod

from flexislack.user_api.message_type import Message


class EventHandler(ABC):
    @abstractmethod
    def handle(self, message: Message):
        pass


