import sys

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution

from group import score_updater

def update_group_stats():
    score_updater.score_update()

def update_strava_stats():
    score_updater.score_update_strava()