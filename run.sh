#!/bin/bash
#set -x
scrdir=`dirname $0`
cd "$scrdir"
# fix model directory for coqui
export TTS_HOME="`pwd`/models"
export PYTHONUNBUFFERED=1
uv run ./tts-server.py "$@" 2>&1
