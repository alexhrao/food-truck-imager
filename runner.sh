#!/bin/bash
# make sure we have latest
if [ $# -lt 1 ]; then
    >&2 echo "Usage: ./runner.sh <location>"
    exit 1
fi
source ./venv/bin/activate
source ./setup.sh
python3 main.py $1 > /dev/null &
cam_pid=$!

while ! lsof -i:10000 > /dev/null ;
do
    sleep 1
done
trap "curl localhost:10000 --silent" EXIT
echo "Listening for changes..."
while :
do
    git fetch
    if ! git diff-index --quiet origin/master --; then
        curl -XGET localhost:10000 --silent
        echo "New changes detected - installing"
        wait $cam_pid
        git pull
        python3 main.py $1 > /dev/null &
        cam_pid=$!
        while ! lsof -i:10000 > /dev/null ;
        do
            sleep 1
        done
        echo "Successfully restarted"
    fi
    sleep 15
done