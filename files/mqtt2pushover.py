#!/usr/bin/env python
import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

from mqttwrapper import run_script


def callback(topic, payload, config):
    configs = config[topic]
    if not isinstance(configs, (list, tuple)):
        configs = [configs]

    for cfg in configs:
        if cfg.get("payload") and payload.decode() != cfg.get("payload"):
            continue

        files = None
        if cfg.get("image_url"):
            try:
                files = {
                    "attachment": (
                        "image.jpeg",
                        requests.get(cfg.get("image_url"), stream=True, timeout=5).raw,
                    )
                }
            except Exception:
                pass

        params = {
            "token": cfg["app_key"],
            "user": cfg["user_key"],
            "message": cfg["message"],
            "sound": cfg.get("sound"),
            "title": cfg.get("title"),
        }
        if cfg.get("devices"):
            params["device"] = cfg["devices"]

        requests.post(
            "https://api.pushover.net/1/messages.json",
            params,
            files=files,
            timeout=5,
        )


def main():
    config = json.loads(os.environ["MQTT_TOPICS_CONFIG"])
    run_script(callback, topics=config.keys(), config=config)


if __name__ == "__main__":
    main()
