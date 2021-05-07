set @caller_folder=%cd%
set @src_folder=%~dp0..\src\sonnen_rennt\

cd %@src_folder%
python manage.py shell
cd %@caller_folder%