set @base_folder=%~dp0..\

pip freeze > %@base_folder%_installation\requirements.txt
