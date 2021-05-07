set @caller_folder=%cd%
set @script_folder=%~dp0

cd %@script_folder%
python _setup.py
cd %@caller_folder%