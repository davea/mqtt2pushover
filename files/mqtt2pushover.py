#!/usr/bin/env python
import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

from mqttwrapper import run_script


def callback(topic, payload, config):
    config = config[topic]

    if config.get("payload") and payload.decode() != config.get("payload"):
        return

    files = None
    if config.get("image_url"):
        try:
            files = {
                "attachment": (
                    "image.jpeg",
                    requests.get(config.get("image_url"), stream=True, timeout=5).raw,
                )
            }
        except Exception:
            pass

    requests.post(
        "https://api.pushover.net/1/messages.json",
        {
            "token": config["app_key"],
            "user": config["user_key"],
            "message": config["message"],
            "sound": config.get("sound"),
            "title": config.get("title"),
        },
        files=files,
        timeout=5,
    )


def main():
    config = json.loads(os.environ["MQTT_TOPICS_CONFIG"])
    run_script(callback, topics=config.keys(), config=config)


if __name__ == "__main__":
    main()
