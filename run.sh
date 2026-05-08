#!/bin/bash
scrdir=`dirname $0`
cd "$scrdir"
uv run ./tts-server.py "$@"
