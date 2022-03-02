from enum import Enum

from django.db import models


class NotificationChoice(Enum):   # A subclass of Enum
    INFO = 0
    WARNING = 1
    ERROR = 2
    SUCCESS = 3


class DashboardNotification(models.Model):
    active = models.BooleanField(default=False)
    # types: 0=info, 1=warning, 2=error, 3=success
    type = models.IntegerField(
        'language',
        choices=[(tag, tag.value) for tag in NotificationChoice]
    )
    msg = models.CharField('msg', max_length=500, null=False, blank=False)
    pos_from_top = models.IntegerField('pos_from_top', default=100)
    publish_by = models.DateTimeField('publish_by', auto_created=True, auto_now=True, blank=False, null=False)
    close_by = models.DateTimeField('close_by', blank=True, null=True)

