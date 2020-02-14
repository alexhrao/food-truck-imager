#!/bin/bash
# make sure we have latest
git pull

source ./venv/bin/activate
source ./setup.sh
python3 main.py $1 &
cam_pid=$!

while :
do
    if ! git diff-index --quiet HEAD --; then
        curl -XGET localhost:10000 --quiet
        echo "New changes detected - installing"
        wait $cam_pid
        git pull
        python3 main.py $1 &
        cam_pid=$!
        echo "Successfully restarted"
    fi
done