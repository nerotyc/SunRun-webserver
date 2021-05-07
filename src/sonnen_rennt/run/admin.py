from django.contrib import admin

from .models import Run, StravaRun


admin.site.register(Run)
admin.site.register(StravaRun)
