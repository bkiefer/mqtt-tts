#!/bin/bash
. utils.sh
docker run --rm \
       -v ./models:/root/.local/share \
       --entrypoint /bin/sh \
       $(getimage) \
       -c "echo \"from TTS.api import TTS; tts = TTS('$1')\" | uv run python "
