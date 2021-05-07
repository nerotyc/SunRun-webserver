set @src_folder=%~dp0..\src\sonnen_rennt\

rmdir /q /s %@src_folder%migrations
rmdir /q /s %@src_folder%__pycache__

rmdir /q /s %@src_folder%api\migrations
rmdir /q /s %@src_folder%api\__pycache__

rmdir /q /s %@src_folder%club\migrations
rmdir /q /s %@src_folder%club\__pycache__

rmdir /q /s %@src_folder%coming_soon\migrations
rmdir /q /s %@src_folder%coming_soon\__pycache__

rmdir /q /s %@src_folder%crawl\migrations
rmdir /q /s %@src_folder%crawl\__pycache__

rmdir /q /s %@src_folder%dashboard\migrations
rmdir /q /s %@src_folder%dashboard\__pycache__

rmdir /q /s %@src_folder%group\migrations
rmdir /q /s %@src_folder%group\__pycache__

rmdir /q /s %@src_folder%route\migrations
rmdir /q /s %@src_folder%route\__pycache__

rmdir /q /s %@src_folder%run\migrations
rmdir /q /s %@src_folder%run\__pycache__

rmdir /q /s %@src_folder%sonnen_rennt\migrations
rmdir /q /s %@src_folder%sonnen_rennt\__pycache__

rmdir /q /s %@src_folder%strava_run\migrations
rmdir /q /s %@src_folder%strava_run\__pycache__

rmdir /q /s %@src_folder%user\migrations
rmdir /q /s %@src_folder%user\__pycache__

rmdir /q /s %@src_folder%utils\migrations
rmdir /q /s %@src_folder%utils\__pycache__
