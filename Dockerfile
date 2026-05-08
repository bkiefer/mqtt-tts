FROM mypy:3.11

WORKDIR /app
COPY gst_tts_source.py mqtt_client.py tts-server.py /app
COPY mytts /app/mytts
COPY pyproject.toml run.sh /app
RUN uv sync
