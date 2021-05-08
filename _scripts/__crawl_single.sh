
CALLER_FOLDER=$(pwd)
SRC_FOLDER="$(dirname $0)""/../src/sonnen_rennt/"

cd $SRC_FOLDER/crawl/
python3 strava_crawler.py
cd $CALLER_FOLDER
