#!/bin/bash
set -x
. utils.sh

if test -z "$1"; then
    echo "Provide a config file!"
    exit 1
fi

docker run --rm -i -t \
       --device /dev/snd --group-add audio \
       -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
       -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
       --add-host host.docker.internal:host-gateway \
       -v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
       -v $HOME/.local/share/tts:/root/.local/share/tts \
       -v ./"$1":/app/config.yml \
       --entrypoint "/bin/bash" \
       $(getimage) \
       -c "./run.sh config.yml"
