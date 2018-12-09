#!/usr/bin/env python3.7
import argparse
from datetime import datetime
from pathlib import Path

import pytz

from slack_notifications.backend.event_provider import EventProvider
from slack_notifications.backend.index import Index
from slack_notifications.backend.run_config import RunConfig
from slack_notifications.backend.slack_api import ApiWrapper
from slack_notifications.simple_event_handler import SimpleEventHandler
from slack_notifications.user_api.message_type import SlackInstance


def run(workspace: Path):
    config = RunConfig(workspace / "config.json")
    if config.secret is None:
        print("secret is not set up. run 'config' to set up.")
        return
    if config.slack is None:
        print("slack instance is not set up. run 'config' to set up.")
        return
    with Index(workspace / "index.json") as index:
        api_wrapper = ApiWrapper(secret=config.secret, slack=config.slack)
        provider = EventProvider(api_wrapper=api_wrapper, local_state=index)
        handler = SimpleEventHandler()
        for conversation, messages in provider.get_new_messages():
            print("%s has %d messages" % (conversation, len(messages)))
            handler.handle(conversation, messages)


def main():
    workspaces_dir = Path(__file__).resolve(strict=True).parent.parent / "workspaces"
    pparser = argparse.ArgumentParser()
    pparser.add_argument("-w", "--workspace", default="default")
    subparsers = pparser.add_subparsers(dest="command")
    subparsers.add_parser("config")
    subparsers.add_parser("clear")
    args = pparser.parse_args()
    if args.command == "config":
        workspace = workspaces_dir / args.workspace
        config = RunConfig(workspace / "config.json")
        slack_name = input("update slack instance (first part of subdomain name of slack.com). current: %s: "
                           % config.slack)
        if slack_name.endswith(".slack.com"):
            slack_name = slack_name[:-len(".slack.com")]
        config.slack = SlackInstance(slack_name)
        print("slack name set to %s." % slack_name)
        if not config.secret:
            print("no api token configured.")
        else:
            print("api token configured. you can update it now.")
        secret = input("provide api token. https://api.slack.com/custom-integrations/legacy-tokens: ")
        config.secret = secret
        print("api token set.")
    elif args.command == "clear":
        with Index(workspaces_dir / args.workspace / "index.json") as index:
            index.set_all(datetime.utcnow().replace(tzinfo=pytz.UTC))
        print("clear successful")
    else:
        run(workspaces_dir / args.workspace)


if __name__ == "__main__":
    main()
