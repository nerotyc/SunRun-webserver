
CALLER_FOLDER=$(pwd)
SCRIPT_FOLDER="$(dirname $0)"

cd $SCRIPT_FOLDER

while true
do
screen -L -S strava_crawler sh __helper_crawl_strava.sh
sleep 20
done

cd $CALLER_FOLDER
