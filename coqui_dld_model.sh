docker run $(getimage) -v./models:/root/.local/share --entrypoint /bin/sh -c \
"echo \"from TTS.api import TTS; tts = TTS('$1')\" | uv run python "
