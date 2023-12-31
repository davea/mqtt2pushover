#!/usr/bin/env python
import os
import sys
import json

import requests
from dotenv import load_dotenv

load_dotenv()

from mqttwrapper import run_script

last_payloads = {}

def json_payload_matches_config(payload, cfg):
    try:
        p = json.loads(payload)
        m = json.loads(cfg.get("payload"))
        if m.items() <= p.items():
            return True
    except json.JSONDecodeError:
        print(f"Invalid JSON payload '{payload}' or match '{cfg.get('payload')}", file=sys.stderr)
    return False


def payload_matches_config(topic, payload, cfg):
    if cfg.get('json', False):
        matches = json_payload_matches_config(payload, cfg)
        if not matches:
            return False
        if cfg.get('change', False):
            # should only notify if the state has changed, i.e. the last
            # payload didn't match
            last_payload = last_payloads.get(topic)
            if not last_payload:
                return True
            if json_payload_matches_config(last_payload, cfg):
                return False
            return True
    elif cfg.get("payload") and payload.decode() != cfg.get("payload"):
        return False
    return True



def callback(topic, payload, config):
    configs = config[topic]
    if not isinstance(configs, (list, tuple)):
        configs = [configs]

    for cfg in configs:
        if not payload_matches_config(topic, payload, cfg):
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
        if cfg.get("priority"):
            params["priority"] = cfg["priority"]

        requests.post(
            "https://api.pushover.net/1/messages.json",
            params,
            files=files,
            timeout=5,
        )

    last_payloads[topic] = payload

def main():
    config = json.loads(os.environ["MQTT_TOPICS_CONFIG"])
    run_script(callback, topics=config.keys(), config=config)


if __name__ == "__main__":
    main()
