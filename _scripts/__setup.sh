#!/bin/sh

CALLER_FOLDER=$(pwd)
SCRIPT_FOLDER="$(dirname $0)"

cd $SCRIPT_FOLDER
python3 _setup.py
cd $CALLER_FOLDER
