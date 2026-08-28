#!/bin/bash
. utils.sh

./update_repo.sh

docker build -f Dockerfile_mypy3_11 -t mypy:3.11 .

docker build --no-cache -f Dockerfile -t "$(getimage)" .
