#!/bin/sh

CALLER_FOLDER=$(pwd)
SRC_FOLDER="$(dirname $0)""/../src/sonnen_rennt/"

cd $SRC_FOLDER/crawl/

while true
do
screen -L -S sonnen_rennt python3 manage.py runserver 0.0.0.0:80
sleep 10
done


cd $CALLER_FOLDER
