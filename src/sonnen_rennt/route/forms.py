from django import forms
from django.core.exceptions import ValidationError

from .models import Route


class RouteCreateForm(forms.ModelForm):

    title = forms.CharField(
        required=True,
        label='Titel',
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'placeholder': "Titel der Route",
            }
        )
    )

    distance = forms.FloatField(
        required=True,
        label='Distanz',
        help_text="Distanz (z.B. 4.2) in km",
    )

    elevation_gain = forms.FloatField(
        label="Höhenmeter",
        required=False,
        help_text=" [m] (leer, falls Route gewählt wird. Standard: 0)"
    )

    link = forms.CharField(
        required=False,
        label='Link zu Wegbeschreibung',
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'placeholder': "Link zu Wegbeschreibung",
            }
        )
    )

    description = forms.CharField(
        required=False,
        label='Beschreibung',
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': "Beschreibung",
            }
        )
    )

    class Meta:
        model = Route
        fields = ['title', 'distance', 'elevation_gain', 'link', 'description']

    def clean_distance(self):
        dist = self.cleaned_data.get('distance')
        if dist > 1000.0:
            raise ValidationError("Routen über 1000km sind nicht zulässig!")
        if dist <= 0:
            raise ValidationError("Routen müssen länger als 0km sein!")
        return dist


    def clean_elevation_gain(self):
        read_elevation_gain = self.cleaned_data.get("elevation_gain")

        if read_elevation_gain is None:
            return 0.0
        if read_elevation_gain > 10000.0:
            raise ValidationError("Aktivitäten über 10.000km sind nicht zulässig!")
        if read_elevation_gain < 0:
            raise ValidationError("Höhenmeter müssen >= 0 sein!")

        return read_elevation_gain


    def create_new(self, user, commit=True):
        instance = Route.objects.create(
            creator=user.profile,

            title=self.cleaned_data.get('title'),
            distance=self.cleaned_data.get('distance'),
            elevation_gain=self.cleaned_data.get('elevation_gain'),
            description=self.cleaned_data.get('description'),
            link=self.cleaned_data.get('link')
        )
        instance.save()
        return instance

    def save_existing(self, user, route):
        route.creator = user.profile

        route.title = self.cleaned_data.get('title')
        route.distance = self.cleaned_data.get('distance')
        route.elevation_gain = self.cleaned_data.get('elevation_gain')

        route.description = self.cleaned_data.get('description')
        route.link = self.cleaned_data.get('link')

        route.save()
        return route
