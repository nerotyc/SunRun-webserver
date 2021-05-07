set @caller_folder=%cd%
set @src_folder=%~dp0..\src\sonnen_rennt\

cd %@src_folder%crawl\
python strava_crawler.py
cd %@caller_folder%
