#!/usr/bin/env python3.7
import argparse
import datetime
import sys
from pathlib import Path

from flexislack.backend.event_provider import EventProvider
from flexislack.user_api.message_type import Message, SlackInstance, Channel
from flexislack.simple_event_handler import SimpleEventHandler


def run(workspace: Path):
    workspace.mkdir(parents=True, exist_ok=True)
    secret = (workspace / "secret.txt").read_text()
    provider = EventProvider(secret, workspace / "index.json")
    for message in provider.get_new_messages():
        pass

def main():
    workspaces_dir = Path(__file__).resolve(strict=True).parent.parent / "workspaces"
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workspace", default="default")
    args = parser.parse_args()
    run(workspaces_dir / args.workspace)


if __name__ == "__main__":
    main()
