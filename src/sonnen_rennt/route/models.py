from django.db import models
from django.urls import reverse
from user.models import Profile


class Route(models.Model):
    creator = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)

    title = models.CharField('title', max_length=250)
    distance = models.FloatField('distance', default=0)
    elevation_gain = models.FloatField('elevation_gain', default=0, null=False, blank=True)   # in meters
    description = models.TextField('description', blank=True, null=True)
    link = models.TextField('link', blank=True, null=True)

    created = models.DateTimeField('created', auto_now=True)

    def __str__(self):
        return "(" + str(self.distance) + " km): " + str(self.title)

    def get_absolute_url(self):
        return f"/route/detail/{self.id}/"
        # return reverse("route:detail", kwargs={"route_id": self.id})

        return f'Route=(name={self.name})'
