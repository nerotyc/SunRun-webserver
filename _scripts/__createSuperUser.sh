
CALLER_FOLDER=$(pwd)
SRC_FOLDER="$(dirname $0)""/../src/sonnen_rennt/"

cd $SRC_FOLDER/crawl/
python manage.py createsuperuser
cd $CALLER_FOLDER
