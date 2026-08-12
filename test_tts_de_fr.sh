#!/bin/bash
set -x

. utils.sh

cleanup() {
    docker kill "$1" 2>/dev/null
    docker container prune -f 2>/dev/null
    exit 1
}

wait_alive() {
    while docker ps -a | grep -q "tts_$1"; do
        sleep 5
    done
}

wait_until_alive() {
    until docker ps -a | grep -q "$1"; do
        sleep 5
    done
}

run() {
    if docker images | grep -q $(getimage); then
        name="tts_$1"
        ./run_docker.sh "$1_docker.yml" "$name" &
        wait_until_alive "$name"
        try=1
        until docker logs "$name" | grep -q 'TTS initialized'; do
            docker logs "$name" 2>&1 >/dev/null || cleanup "$name"
            echo -n $try
            try=$(($try+1))
            sleep 5
        done
    else
        ./run.sh "$1.yml" | tee log.log &
        until grep -q 'TTS initialized' log.log; do
            echo -n $try
            try=$(($try+1))
            sleep 5
        done
        rm log.log
    fi
}

rm log.log 2>&1
if test -z "$1" -o "$1" = "-d"; then
    run de_config
    uv run mqtt_client.py -t tts/behaviour '{ "id": 0, "text": "Das ist ein von Martin gesprochener Text" }'
    uv run mqtt_client.py -t tts/control "exit"
    wait_alive de_config
fi

if test -z "$1" -o "$1" = "-f"; then
    run fr_config
    uv run mqtt_client.py -t tts/behaviour '{ "id": 0, "text": "C'\''est un texte rit d'\''une femme virtuelle pour vous seule." }'
    uv run mqtt_client.py -t tts/control "exit"
fi
