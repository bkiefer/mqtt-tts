#!/bin/bash
#set -x
. utils.sh

if test -z "$1"; then
    echo "Provide a config file!"
    exit 1
fi
if test -n "$2"; then
    name="--name $2"
else
    name="--name tts_server"
fi
docker run --rm $name \
       --device /dev/snd --group-add audio \
       -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
       --add-host host.docker.internal:host-gateway \
       -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
       -v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
       -v ./models:/app/models \
       -v ./"$1":/app/config.yml \
       $(getimage) \
       /bin/bash -c "./run.sh config.yml"
