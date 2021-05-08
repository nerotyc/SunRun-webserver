
CALLER_FOLDER=$(pwd)
SRC_FOLDER="$(dirname $0)""/../src/sonnen_rennt/"

cd $SRC_FOLDER/crawl/

python3 manage.py makemigrations
python3 manage.py makemigrations api
python3 manage.py makemigrations club
python3 manage.py makemigrations coming_soon
python3 manage.py makemigrations crawl
python3 manage.py makemigrations dashboard
python3 manage.py makemigrations group
python3 manage.py makemigrations run
python3 manage.py makemigrations strava_run
python3 manage.py makemigrations user

python3 manage.py migrate
#python3 manage.py migrate --fake-initial

cd $CALLER_FOLDER
