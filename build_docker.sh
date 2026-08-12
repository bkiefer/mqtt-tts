#!/bin/bash
. utils.sh

./update_repo.sh

docker build --no-cache -f Dockerfile -t "$(getimage)" .
