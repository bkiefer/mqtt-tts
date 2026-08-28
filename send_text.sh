#!/bin/bash

if test -z "$1"; then
    text="Das ist ein wirklich total unsinniger Text."
else
    text="$1"
fi

uv run python mqtt_client.py -t 'tts/behaviour' '{ "id": 222, "text": "'"$text"'" }'
