FROM mypy:3.11

WORKDIR /app
COPY coqui.py gst_tts_source.py kikiri.py mqtt_client.py tts-server.py /app
COPY mytts /app/mytts
COPY kikiri-tts /app/kikiri-tts
COPY pyproject.toml run.sh /app
RUN uv sync
