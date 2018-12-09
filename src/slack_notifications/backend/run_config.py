import json
from pathlib import Path
from typing import Optional

from slack_notifications.user_api.message_type import SlackInstance


class RunConfig:
    def __init__(self, path: Path):
        self._path = path
        self._data = {}

    def _reload(self):
        if not self._path.exists():
            self._path.parent.mkdir(exist_ok=True, parents=True)
            self._rewrite()
        self._data = json.load(self._path.open("r"))

    def _rewrite(self):
        json.dump(self._data, self._path.open("w"), indent=4)

    @property
    def slack(self) -> SlackInstance:
        self._reload()
        return SlackInstance(self._data['slack']) if "slack" in self._data else None

    @slack.setter
    def slack(self, slack: SlackInstance):
        self._data['slack'] = slack.name
        self._rewrite()

    @property
    def secret(self) -> Optional[str]:
        self._reload()
        return self._data.get('secret') if "secret" in self._data else None

    @secret.setter
    def secret(self, secret: str):
        self._data['secret'] = secret
        self._rewrite()
