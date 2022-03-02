from datetime import datetime, timedelta, timezone
from os import read

import pytz
from django import forms
from django.core.exceptions import ValidationError

from route.models import Route
from group.models import Group
from run.models import Run

from utils.formfields import NT_DateTimeInput


class RunCreateEditForm(forms.ModelForm):
    distance = forms.FloatField(
        label="Distanz",
        required=False,
        help_text=" [km] (leer, falls Route gewählt wird.)"
    )

    elevation_gain = forms.FloatField(
        label="Höhenmeter",
        required=False,
        help_text=" [m] (leer, falls Route gewählt wird. Standard: 0)"
    )

    type = forms.TypedChoiceField(
        label="Aktivitätstyp",
        required=True,
        initial=Run.TYPE_RUN,
        choices=Run.TYPE_CHOICES,
    )

    time_start = forms.DateTimeField(
        label="Startzeit",
        required=False,
        input_formats=["%d.%m.%Y %H:%M:%S"],
        # input_formats=["%d-%m-%Y %H:%M"],
        help_text=" ⇽ hier klicken (leer für JETZT)",
        widget=NT_DateTimeInput()
    )

    duration = forms.DurationField(
        label="Dauer*",
        required=True,
        help_text="Format: 01:05:12 (Stunden:Minuten:Sekunden)",
    )

    note = forms.CharField(
        required=False,
        label='Notiz',
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': "Notiz",
            }
        )
    )

    # group = forms.ModelMultipleChoiceField(
    #     label="Gruppe",
    #     required=False,
    #     help_text="Lauf einer Gruppe hinzufügen",
    #     queryset=Group.objects.all()
    #     # choices=Group.objects.all()
    # )

    # group = forms.ChoiceField(
    #     required=False,
    #     help_text="Lauf einer Gruppe hinzufügen",
    #     choices=Group.objects.all()
    # )

    # # TODO only show own
    # def __init__(self, user):
    #     # print("form_init")
    #     # self.user = user
    #     # print("user.profile.id", user.profile.id)
    #     #
    #     # self.route = forms.ModelMultipleChoiceField(
    #     #     queryset=Route.objects.filter(creator=user.profile.id)
    #     # )
    #     # filter(creator=user.profile.id)
    #     # self.route = route
    #     super().__init__()

    class Meta:
        model = Run
        fields = ['route', 'distance', 'elevation_gain', 'type', 'time_start', 'duration', 'group', 'note']
        # widgets = {
        #     'time_start': NT_DateTimeInput(
        #     ),
        # }

    def create_new(self, user, commit=True):
        instance = Run.objects.create(
            creator=user.profile,

            distance=self.cleaned_data.get('distance'),
            elevation_gain=self.cleaned_data.get('elevation_gain'),
            route=self.cleaned_data.get('route'),

            time_start=self.cleaned_data.get('time_start'),
            duration=self.cleaned_data.get('duration'),
            group=self.cleaned_data.get('group'),

            type=self.cleaned_data.get('type'),

            note=self.cleaned_data.get('note')
        )
        # instance.save()
        return instance

    def save_existing(self, user, run):
        run.creator = user.profile

        run.distance = self.cleaned_data.get('distance')
        run.elevation_gain = self.cleaned_data.get('elevation_gain')
        run.route = self.cleaned_data.get('route')

        run.time_start = self.cleaned_data.get('time_start')
        run.duration = self.cleaned_data.get('duration')
        run.group = self.cleaned_data.get('group')

        run.type = self.cleaned_data.get('type')

        run.note = self.cleaned_data.get('note')

        run.save()
        return run

    def clean_time_start(self):
        read_time = self.cleaned_data.get("time_start")

        if read_time is None:
            dtt_now = datetime.now(tz=pytz.timezone("Europe/Berlin"))  # berlin tz
            return dtt_now
        else:
            read_time = pytz.timezone("Europe/Berlin").localize(read_time.replace(tzinfo=None))  # berlin tz

        today = datetime.now(tz=timezone.utc)
        one_week = timedelta(weeks=1)
        read_time_utc = pytz.utc.normalize(read_time)  # utc time

        delta = today - read_time_utc

        if delta > one_week:
            raise ValidationError("Startzeit darf nicht länger als 7 Tage zurückliegen!")

        # if read_time > today:
        #     raise ValidationError("Startzeit darf nicht in der Zukunft liegen!")

        return read_time_utc

    def clean_distance(self):
        read_distance = self.cleaned_data.get("distance")
        read_route = self.cleaned_data.get("route")
        if read_route:
            return read_route.distance

        if read_distance is None:
            raise ValidationError("Distanz darf nicht leer sein, wenn keine Route gewählt ist.")

        if read_distance > 1000.0:
            raise ValidationError("Aktivitäten über 5000km sind nicht zulässig!")
        if read_distance <= 0:
            raise ValidationError("Aktivitäten müssen länger als 0km sein!")

        return read_distance

    def clean_elevation_gain(self):
        read_elevation_gain = self.cleaned_data.get("elevation_gain")
        read_route = self.cleaned_data.get("route")
        if read_route:
            return read_route.elevation_gain

        if read_elevation_gain is None:
            return 0.0

        if read_elevation_gain > 10000.0:
            raise ValidationError("Aktivitäten über 10.000km sind nicht zulässig!")
        if read_elevation_gain < 0:
            raise ValidationError("Höhenmeter müssen >= 0 sein!")

        return read_elevation_gain

    # def clean_group(self):
    #     group = self.cleaned_data.get('group')
    #     queried_group = Group.objects.get(id=group.id)
    #     return queried_group
    #
    # def clean_route(self):
    #     route = self.cleaned_data.get('route')
    #     queried_route = Route.objects.get(id=route.id)
    #     return queried_route


# copy of RunCreateEditForm with default for time_start
class RunEditForm(forms.ModelForm):
    distance = forms.FloatField(
        label="Distanz",
        required=False,
        help_text="(Kann leergelassen werden, wenn Route gewählt wird.)"
    )

    elevation_gain = forms.FloatField(
        label="Höhenmeter",
        required=False,
        help_text=" [m] (leer, falls Route gewählt wird. Standard: 0)"
    )

    type = forms.TypedChoiceField(
        label="Aktivitätstyp",
        required=True,
        initial=Run.TYPE_RUN,
        choices=Run.TYPE_CHOICES,
    )

    # TODO default with datetimepicker here!
    time_start = forms.DateTimeField(
        label="Startzeit",
        required=False,
        input_formats = ["%d.%m.%Y %H:%M:%S"],
        # input_formats=["%d.%m.%Y %H:%M"],
        help_text=" (Format: 'dd.mm.yyyy hh.mm.ss' Bsp.: 30.12.1959 23:58:59)",
    )

    duration = forms.DurationField(
        label="Dauer",
        required=True,
        help_text="Format: 01:05:12 (Stunden:Minuten:Sekunden)",
    )

    note = forms.CharField(
        required=False,
        label='Notiz',
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': "Notiz",
            }
        )
    )

    # group = forms.ModelMultipleChoiceField(
    #     label="Gruppe",
    #     required=False,
    #     help_text="Lauf einer Gruppe hinzufügen",
    #     queryset=Group.objects.all()
    #     # choices=Group.objects.all()
    # )

    # group = forms.ChoiceField(
    #     required=False,
    #     help_text="Lauf einer Gruppe hinzufügen",
    #     choices=Group.objects.all()
    # )

    # # TODO only show own
    # def __init__(self, user):
    #     # print("form_init")
    #     # self.user = user
    #     # print("user.profile.id", user.profile.id)
    #     #
    #     # self.route = forms.ModelMultipleChoiceField(
    #     #     queryset=Route.objects.filter(creator=user.profile.id)
    #     # )
    #     # filter(creator=user.profile.id)
    #     # self.route = route
    #     super().__init__()

    class Meta:
        model = Run

        fields = ['route', 'distance', 'elevation_gain', 'type', 'time_start', 'duration', 'group', 'note']
        # widgets = {
        #     'time_start': NT_DateTimeInput(
        #     ),
        # }

    def create_new(self, user, commit=True):
        instance = Run.objects.create(
            creator=user.profile,

            distance=self.cleaned_data.get('distance'),
            elevation_gain=self.cleaned_data.get('elevation_gain'),
            route=self.cleaned_data.get('route'),

            time_start=self.cleaned_data.get('time_start'),
            duration=self.cleaned_data.get('duration'),
            group=self.cleaned_data.get('group'),

            type=self.cleaned_data.get('type'),

            note=self.cleaned_data.get('note')
        )
        # instance.save()
        return instance

    def save_existing(self, user, run):
        run.creator = user.profile

        run.distance = self.cleaned_data.get('distance')
        run.elevation_gain = self.cleaned_data.get('elevation_gain')
        run.route = self.cleaned_data.get('route')

        run.time_start = self.cleaned_data.get('time_start')
        run.duration = self.cleaned_data.get('duration')
        run.group = self.cleaned_data.get('group')

        run.type = self.cleaned_data.get('type')

        run.note = self.cleaned_data.get('note')

        run.save()
        return run


    def clean_time_start(self):
        read_time = self.cleaned_data.get("time_start")

        if read_time is None:
            dtt_now = datetime.now(tz=pytz.timezone("Europe/Berlin"))  # berlin tz
            return dtt_now
        else:
            read_time = pytz.timezone("Europe/Berlin").localize(read_time.replace(tzinfo=None))  # berlin tz

        today = datetime.now(tz=timezone.utc)
        one_week = timedelta(weeks=1)
        read_time_utc = pytz.utc.normalize(read_time)  # utc time

        delta = today - read_time_utc

        if delta > one_week:
            raise ValidationError("Startzeit darf nicht länger als 7 Tage zurückliegen!")

        # if read_time > today:
        #     raise ValidationError("Startzeit darf nicht in der Zukunft liegen!")

        return read_time_utc

    def clean_distance(self):
        read_distance = self.cleaned_data.get("distance")
        read_route = self.cleaned_data.get("route")
        if read_route:
            return read_route.distance

        if read_distance is None:
            raise ValidationError("Distanz darf nicht leer sein, wenn keine Route gewählt ist.")

        if read_distance > 1000.0:
            raise ValidationError("Aktivitäten über 1000km sind nicht zulässig!")
        if read_distance <= 0:
            raise ValidationError("Aktivitäten müssen länger als 0km sein!")

        return read_distance


    def clean_elevation_gain(self):
        read_elevation_gain = self.cleaned_data.get("elevation_gain")
        read_route = self.cleaned_data.get("route")
        if read_route:
            return read_route.elevation_gain

        if read_elevation_gain is None:
            return 0.0

        if read_elevation_gain > 10000.0:
            raise ValidationError("Aktivitäten über 10.000km sind nicht zulässig!")
        if read_elevation_gain < 0:
            raise ValidationError("Höhenmeter müssen >= 0 sein!")

        return read_elevation_gain


    # def clean_group(self):
    #     group = self.cleaned_data.get('group')
    #     queried_group = Group.objects.get(id=group.id)
    #     return queried_group
    #
    # def clean_route(self):
    #     route = self.cleaned_data.get('route')
    #     queried_route = Route.objects.get(id=route.id)
    #     return queried_route


# def clean_note(self, *args, **kwargs):
#     note = self.cleaned_data.get("note")
#     if 'test' not in note:
#         raise forms.ValidationError("Errormessage")
#     return note


# class RawRunCreateForm(forms.Form):
#     time_start = forms.DateTimeField(
#         required=False,
#         widget=forms.DateTimeInput(
#             attrs={
#                 # 'is_hidden': False,
#                 # 'placeholder': "Startzeit (leer für Jetzt-Dauer)",
#                 'class': 'form-control datetimepicker-input',
#                 'data-target': '#datetimepicker1'
#             }
#         ),
#         input_formats=['%d/%m/%Y %H:%M'],
#     )
# duration = forms.DurationField(required=True, widget=forms.TimeInput(
#     attrs={
#         'is_hidden': False,
#         'placeholder': "Dauer",
#     }
# ))  # "Dauer",
# note = forms.CharField(required=False, widget=forms.Textarea(
#     attrs={
#         'class': 'todoclass',
#         'rows': 10,
#         'placeholder': "Notiz",
#     }
# ))  # "Notiz",
