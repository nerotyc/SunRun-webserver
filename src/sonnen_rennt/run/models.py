from django.db import models
from django.urls import reverse
from django.db.models.query import QuerySet
from django_group_by import GroupByMixin

from route.models import Route
from user.models import Profile
from group.models import Group

# null or default for optional fields (blank=True --> can be left out)
# null -> database
# blank -> rendered field


class RunQuerySet(QuerySet, GroupByMixin):
    pass


# TYPE_WALK, TYPE_RUN, TYPE_EBIKE, TYPE_BIKE
def run_get_score_scale(type):
    if type == Run.TYPE_WALK:
        return 1.0/3.0 + 1.0
    elif type == Run.TYPE_RUN:
        return 1.0
    elif type == Run.TYPE_BIKE:
        return 2.0/3.0
    elif type == Run.TYPE_EBIKE:
        return 1.0/3.0


class Run(models.Model):
    objects = RunQuerySet.as_manager()

    creator = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)

    distance = models.FloatField('distance', null=False)    # in kilometers
    elevation_gain = models.FloatField('elevation_gain', default=0, null=False, blank=True)   # in meters
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, blank=True, null=True)

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)

    time_start = models.DateTimeField('time_start')  # , auto_now=True
    duration = models.DurationField('duration')

    TYPE_WALK = "WALK"
    TYPE_RUN = "RUN"
    TYPE_BIKE = "BIKE"
    TYPE_EBIKE = "E-BIKE"

    TYPE_CHOICES = (
        (TYPE_WALK, 'Gehen'),
        (TYPE_RUN, 'Laufen'),
        (TYPE_BIKE, 'Rad'),
        (TYPE_EBIKE, 'E-Bike')
    )

    type = models.CharField('type', max_length=50, default=TYPE_CHOICES, choices=TYPE_CHOICES)

    note = models.TextField('note', blank=True, null=True)

    def __str__(self):
        return "RunObject=(time_start: " + str(self.time_start) + ", duration:" + str(self.duration) + ")"

    def get_absolute_url(self):
        return reverse("run:detail", kwargs={"run_id": self.id})

# {
#   "athlete": {
#     "resource_state": 2,
#     "firstname": "Konrad",
#     "lastname": "E."
#   },
#   "name": "Lauf am Nachmittag",
#   "distance": 5862.2,
#   "moving_time": 1936,
#   "elapsed_time": 1936,
#   "total_elevation_gain": 174,
#   "type": "Run",
# }


class StravaRun(models.Model):
    objects = RunQuerySet.as_manager()

    creator = models.CharField('creator', default="unbekannt", blank=True, null=False, max_length=300)

    strava_handle = models.PositiveBigIntegerField('strava_handle', unique=True, blank=None, null=False)
    profile_handle = models.PositiveBigIntegerField('profile_handle', blank=True, null=True)
    route_handle = models.PositiveBigIntegerField('route_handle', blank=True, null=True)

    distance = models.FloatField('distance', null=False)    # in kilometers
    elevation_gain = models.FloatField('elevation_gain', default=0, null=False, blank=True)   # in meters

    time_start = models.DateTimeField('time_start')
    duration = models.DurationField('duration')  # strava_run.elapsed_time

    type = models.CharField('type', max_length=50, default=Run.TYPE_RUN, choices=Run.TYPE_CHOICES)

    note = models.CharField('note', blank=True, null=True, max_length=2000)  # strava_run.name

    def __str__(self):
        return "RunObject=(creator: " + self.creator + ", duration:" + str(self.duration) + ")"

    def get_absolute_url(self):
        return reverse("strava_run:detail", kwargs={"run_id": self.id})
