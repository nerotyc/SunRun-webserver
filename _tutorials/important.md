# COMMANDS

## models:
usable fields
https://docs.djangoproject.com/en/3.1/ref/models/fields/

```
python manage.py shell
from run.models import Run
Run.objects.all()
Run.objects.create(field=value, field2=value2)
```


### use appropriate selenium driver: 
```/crawl/x```

### strava login:

```
/crawl/login.conf:
strava_email: x
strava_password: x
```

### Running strava crawler

```
/src/sonnen_rennt/:
python3
from crawl import strava_crawler
strava_crawler.fetch_insert_strava_runs()
```


## Fake migrations
https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html