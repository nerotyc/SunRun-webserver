
import os
import yaml

from datetime import timedelta

from django.db.models import Sum

from django.shortcuts import render
from django.contrib import messages

from group.models import Group
from run.models import Run, run_get_score_scale, StravaRun


class GroupScore:
    def __init__(
            self,
            run_count,
            num_participants,
            sum_distance_walk,
            sum_distance_run,
            sum_distance_bike,
            sum_distance_ebike,
            sum_duration,
            score_value):
        self.run_count = run_count
        self.num_participants = num_participants
        self.sum_distance_walk = sum_distance_walk
        self.sum_distance_run = sum_distance_run
        self.sum_distance_bike = sum_distance_bike
        self.sum_distance_ebike = sum_distance_ebike
        self.sum_duration = sum_duration
        self.score_value = score_value


# [Strava Conf]---------------------------------------------

strava_score = GroupScore(0, 0, 0, 0, 0, 0, 0, 0)


def read_strava_data():
    global strava_score

    if str(os.getcwd()).split("\\")[-1] == 'crawl':
        file_path = '../group/strava_group_data.yml'
    else:
        file_path = 'group/strava_group_data.yml'

    with open(file_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if data:
            score = data['score']
            run_count = data['run_count']
            num_participants = data['num_participants']
            sum_duration = data['sum_duration']
            sum_distance_walk = data['sum_distance_walk']
            sum_distance_run = data['sum_distance_run']
            sum_distance_bike = data['sum_distance_bike']
            sum_distance_ebike = data['sum_distance_ebike']

            return GroupScore(
                run_count,
                num_participants,
                sum_distance_walk,
                sum_distance_run,
                sum_distance_bike,
                sum_distance_ebike,
                sum_duration,
                score
            )
        else:
            print('reading strava data failed!')
        return GroupScore(0, 0, 0, 0,
                          0, 0, 0, 0)


def _write_strava_data(group_score: GroupScore):
    global strava_score

    if str(os.getcwd()).split("\\")[-1] == 'crawl':
        file_path = '../group/strava_group_data.yml'
    else:
        file_path = 'group/strava_group_data.yml'

    with open(file_path, 'w+') as f:
        data = {
            'score': group_score.score_value,
            'run_count': group_score.run_count,
            'num_participants': group_score.num_participants,
            'sum_duration': group_score.sum_duration,
            'sum_distance_walk': group_score.sum_distance_walk,
            'sum_distance_run': group_score.sum_distance_run,
            'sum_distance_bike': group_score.sum_distance_bike,
            'sum_distance_ebike': group_score.sum_distance_ebike,
        }
        yaml.dump(data, f)


def _calculate_strava_score():
    group_runs = StravaRun.objects.all()
    run_count = group_runs.count()
    num_participants = group_runs.values('creator').distinct().count()
    # num_participants = group_runs.annotate(Count('informationunit__creator', distinct=True))
    # print(group_runs.values('creator').annotate(count=Count('id', distrinct=True)).order_by())

    sum_distance_walk = group_runs.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_walk is None:
        sum_distance_walk = 0

    sum_distance_run = group_runs.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_run is None:
        sum_distance_run = 0

    sum_distance_bike = group_runs.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_bike is None:
        sum_distance_bike = 0

    sum_distance_ebike = group_runs.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_ebike is None:
        sum_distance_ebike = 0

    sum_duration_time = group_runs.aggregate(Sum('duration')).get('duration__sum')  # group_runs.aggregate(Sum('duration')).get('duration__sum')
    if sum_duration_time is None:
        sum_duration_time = timedelta(seconds=0)
    sum_duration = float(sum_duration_time.seconds) / 3600
    score_value = score_of(sum_distance_walk, sum_distance_run, sum_distance_bike, sum_distance_ebike)

    return GroupScore(
        run_count,
        num_participants,
        sum_distance_walk,
        sum_distance_run,
        sum_distance_bike,
        sum_distance_ebike,
        sum_duration,
        score_value
    )


def score_update_strava():
    global strava_score

    strava_score = _calculate_strava_score()
    _write_strava_data(strava_score)

# ----------------------------------------------------------


def update_view(request):
    score_update()
    messages.success(request, "updated group scores")
    return render(request, "root.html", {})


def score_update():
    queried_groups = Group.objects.all()

    for group in queried_groups:
        group_scoring = calculate_group_score(group)
        group.run_count = group_scoring.run_count
        group.num_participants = group_scoring.num_participants
        group.sum_duration = group_scoring.sum_duration  # TODO
        group.sum_distance_walk = group_scoring.sum_distance_walk
        group.sum_distance_run = group_scoring.sum_distance_run
        group.sum_distance_bike = group_scoring.sum_distance_bike
        group.sum_distance_ebike = group_scoring.sum_distance_ebike
        group.score = group_scoring.score_value
        group.save()


def calculate_group_score(group):
    group_runs = Run.objects.filter(group=group)
    run_count = group_runs.count()
    num_participants = group_runs.values('creator').distinct().count()
    # num_participants = group_runs.annotate(Count('informationunit__creator', distinct=True))
    # print(group_runs.values('creator').annotate(count=Count('id', distrinct=True)).order_by())

    sum_distance_walk = group_runs.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_walk is None:
        sum_distance_walk = 0

    sum_distance_run = group_runs.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_run is None:
        sum_distance_run = 0

    sum_distance_bike = group_runs.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_bike is None:
        sum_distance_bike = 0

    sum_distance_ebike = group_runs.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')
    if sum_distance_ebike is None:
        sum_distance_ebike = 0

    sum_duration_time = group_runs.aggregate(Sum('duration')).get('duration__sum')  # group_runs.aggregate(Sum('duration')).get('duration__sum')
    if sum_duration_time is None:
        sum_duration_time = timedelta(seconds=0)
    sum_duration = float(sum_duration_time.seconds) / 3600
    score_value = score_of(sum_distance_walk, sum_distance_run, sum_distance_bike, sum_distance_ebike)

    return GroupScore(
        run_count,
        num_participants,
        sum_distance_walk,
        sum_distance_run,
        sum_distance_bike,
        sum_distance_ebike,
        sum_duration,
        score_value
    )


# def score_of(participants, hours, kilometers):
#     score_participants = -3430 * (1 / (participants + 95)) + 36.5
#     score_distance = -129800 * (1 / (kilometers + 4000)) + 32.5
#     score_duration = -1724000 * (1 / (hours + 39600)) + 44
#     return score_duration + score_distance + score_participants

def score_of(walk, run, bike, ebike):
    return walk * run_get_score_scale(Run.TYPE_WALK) \
           + run * run_get_score_scale(Run.TYPE_RUN) \
           + bike * run_get_score_scale(Run.TYPE_BIKE) \
           + ebike * run_get_score_scale(Run.TYPE_EBIKE)
