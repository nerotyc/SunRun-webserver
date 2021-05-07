set @caller_folder=%cd%
set @src_folder=%~dp0..\src\sonnen_rennt\

cd %@src_folder%
python manage.py runserver 0.0.0.0:8000
cd %@caller_folder%
