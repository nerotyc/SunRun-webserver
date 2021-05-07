set @caller_folder=%cd%
set @src_folder=%~dp0..\src\sonnen_rennt\

cd %@src_folder%

python manage.py makemigrations
python manage.py makemigrations api
python manage.py makemigrations club
python manage.py makemigrations coming_soon
python manage.py makemigrations crawl
python manage.py makemigrations dashboard
python manage.py makemigrations group
python manage.py makemigrations run
python manage.py makemigrations strava_run
python manage.py makemigrations user

python manage.py migrate

cd %@caller_folder%
