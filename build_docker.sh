#!/bin/bash
docker images 2>&1 | grep -q mypy:3.11 ||
    docker build -f Dockerfile_mypy3_11 -t mypy:3.11 .

. utils.sh

while getopts u c
do
    case $c in
        u)  update="true" ;;
        *)  echo "Usage: $0 [-<u>pdate_repo]

update will pull the git repository and all subrepositories recursively
"
    esac
done
shift `expr $OPTIND - 1`

if test -n "$update" ; then # check out and update all modules
   ./update_repo.sh
fi

docker build --no-cache -f Dockerfile -t "$(getimage)" .
