#!/bin/bash
scrdir=`dirname $0`
cd "$scrdir"
PYTHONUNBUFFERED=1 uv run ./tts-server.py "$@" 2>&1
