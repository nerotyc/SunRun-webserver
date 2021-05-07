from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField

from user.models import Profile

class Group(models.Model):

    creator = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)

    name = models.CharField('name', max_length=250)
    description = models.TextField('description', blank=True, null=True)

    score = models.FloatField('score', blank=True, default=0)
    run_count = models.IntegerField('run_count', blank=True, default=0)
    num_participants = models.IntegerField('num_participants', blank=True, default=0)
    sum_duration = models.FloatField('sum_duration', blank=True, default=0)
    sum_distance_walk = models.FloatField('sum_distance_walk', blank=True, default=0)
    sum_distance_run = models.FloatField('sum_distance_run', blank=True, default=0)
    sum_distance_bike = models.FloatField('sum_distance_bike', blank=True, default=0)
    sum_distance_ebike = models.FloatField('sum_distance_ebike', blank=True, default=0)

    # CLOSED = 1
    # EN_INV_DIS_REQ = 2
    # EN_INV_EN_REQ = 3
    # OPEN = 4
    #
    # GROUP_MODE_CHOICES = (
    #     (CLOSED, 'Closed'),
    #     (EN_INV_DIS_REQ, 'InvitationPrivat'),
    #     (EN_INV_EN_REQ, 'RequestPrivat'),
    #     (OPEN, 'Open'),
    # )
    #
    # mode = MultiSelectField('mode',
    #                         max_choices=1,
    #                         choices=GROUP_MODE_CHOICES,
    #                         default=CLOSED,
    #                   # blank=True,
    #                   # null=True,
    #                   )

    created = models.DateTimeField('created', auto_now=True)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return f"/group/detail/{self.id}/"
        # return reverse("route:detail", kwargs={"route_id": self.id})
