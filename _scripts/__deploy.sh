#!/bin/sh

CALLER_FOLDER=$(pwd)
BASE_FOLDER="$(dirname $0)""/../"

pip freeze > $BASE_FOLDER/_installation/requirements.txt
