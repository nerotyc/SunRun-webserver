CALLER_FOLDER=$(pwd)
SRC_FOLDER="$(dirname $0)""/../src/sonnen_rennt/"

cd $SRC_FOLDER/crawl/

while true
do
        echo "start daily crawling job...";
        python3 strava_crawler.py;
        echo "finished daily crawling job.";
        sleep 86400
done

cd $CALLER_FOLDER
