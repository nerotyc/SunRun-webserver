from datetime import datetime, timedelta

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from dashboard.models import DashboardNotification, NotificationChoice
from group.score_updater import score_of
from run.models import Run, StravaRun

goal_community_month = 15000


class StatsRow:

    def __init__(
            self,
            distance_walk,
            distance_run,
            distance_bike,
            distance_ebike,
            count,
            duration,
            score
    ):
        self.distance_walk = distance_walk
        self.distance_run = distance_run
        self.distance_bike = distance_bike
        self.distance_ebike = distance_ebike
        self.count = count
        self.duration = duration
        self.score = score


def default_view(request, *args, **kargs):
    today = datetime.today()

    # DAY ##################################
    day_filtered = Run.objects.filter(
        time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    day_count = day_filtered.count()
    day_duration = day_filtered.aggregate(Sum('duration')).get('duration__sum')

    day_distance_walk = day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    day_distance_run = day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    day_distance_bike = day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    day_distance_ebike = day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if day_count is None:
        day_count = 0
    if day_duration is None:
        day_duration = timedelta(seconds=0)

    if day_distance_walk is None:
        day_distance_walk = 0
    if day_distance_run is None:
        day_distance_run = 0
    if day_distance_bike is None:
        day_distance_bike = 0
    if day_distance_ebike is None:
        day_distance_ebike = 0

    day_distance_score = score_of(day_distance_walk, day_distance_run, day_distance_bike, day_distance_ebike)

    # MONTH ##################################
    month_filtered = Run.objects.filter(time_start__gte=datetime(year=today.year, month=today.month, day=1))

    month_count = month_filtered.count()
    month_duration = month_filtered.aggregate(Sum('duration')).get('duration__sum')

    month_distance_walk = month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    month_distance_run = month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    month_distance_bike = month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    month_distance_ebike = month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if month_count is None:
        month_count = 0
    if month_duration is None:
        month_duration = timedelta(seconds=0)

    if month_distance_walk is None:
        month_distance_walk = 0
    if month_distance_run is None:
        month_distance_run = 0
    if month_distance_bike is None:
        month_distance_bike = 0
    if month_distance_ebike is None:
        month_distance_ebike = 0

    month_distance_score = score_of(month_distance_walk, month_distance_run, month_distance_bike, month_distance_ebike)

    ##################################################################################
    # Strava Data ####################################################################

    strava_day_filtered = StravaRun.objects.filter(
        time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    strava_day_count = strava_day_filtered.count()
    strava_day_duration = strava_day_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_day_distance_walk = strava_day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_run = strava_day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_bike = strava_day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_ebike = strava_day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_day_count is None:
        strava_day_count = 0
    if strava_day_duration is None:
        strava_day_duration = timedelta(seconds=0)

    if strava_day_distance_walk is None:
        strava_day_distance_walk = 0
    if strava_day_distance_run is None:
        strava_day_distance_run = 0
    if strava_day_distance_bike is None:
        strava_day_distance_bike = 0
    if strava_day_distance_ebike is None:
        strava_day_distance_ebike = 0

    strava_day_distance_score = score_of(strava_day_distance_walk, strava_day_distance_run,
                                         strava_day_distance_bike, strava_day_distance_ebike)

    #########################################

    strava_month_filtered = StravaRun.objects.filter(
        time_start__gte=datetime(year=today.year, month=today.month, day=1))

    strava_month_count = strava_month_filtered.count()
    strava_month_duration = strava_month_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_month_distance_walk = strava_month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_run = strava_month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_bike = strava_month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_ebike = strava_month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_month_count is None:
        strava_month_count = 0
    if strava_month_duration is None:
        strava_month_duration = timedelta(seconds=0)

    if strava_month_distance_walk is None:
        strava_month_distance_walk = 0
    if strava_month_distance_run is None:
        strava_month_distance_run = 0
    if strava_month_distance_bike is None:
        strava_month_distance_bike = 0
    if strava_month_distance_ebike is None:
        strava_month_distance_ebike = 0

    strava_month_distance_score = score_of(strava_month_distance_walk, strava_month_distance_run,
                                           strava_month_distance_bike, strava_month_distance_ebike)

    ##################################################################################
    ##################################################################################

    community_month_score_sum = (month_distance_score + strava_month_distance_score)
    monthly_percentage = str(int((community_month_score_sum * 100.0 / goal_community_month)))

    context = {
        'community_stats_day': StatsRow(
            '% 6.0f' % (day_distance_walk + strava_day_distance_walk) + ' km',
            '% 6.0f' % (day_distance_run + strava_day_distance_run) + ' km',
            '% 6.0f' % (day_distance_bike + strava_day_distance_bike) + ' km',
            '% 6.0f' % (day_distance_ebike + strava_day_distance_ebike) + ' km',
            f'{(day_count + strava_day_count)}',
            str(day_duration + strava_day_duration).split(':')[0] + " h",
            (day_distance_score + strava_day_distance_score),
        ),
        'stats_community_month_progressbar_text':
            monthly_percentage + " %" +
            " (" + str(int(community_month_score_sum)) + "/" + str(int(goal_community_month)) + " km)",
        'stats_community_month_progressbar_percent': monthly_percentage,
        'community_stats_month': StatsRow(
            '% 6.0f' % (month_distance_walk + strava_month_distance_walk) + ' km',
            '% 6.0f' % (month_distance_run + strava_month_distance_run) + ' km',
            '% 6.0f' % (month_distance_bike + strava_month_distance_bike) + ' km',
            '% 6.0f' % (month_distance_ebike + strava_month_distance_ebike) + ' km',
            f'{(month_count + strava_month_count)}',
            str(month_duration + strava_month_duration).split(':')[0] + " h",
            (month_distance_score + strava_month_distance_score),
        ),
    }

    if request.user.is_authenticated:

        # DAY ##################################
        day_filtered = Run.objects.filter(creator=request.user.profile) \
            .filter(time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

        day_count = day_filtered.count()
        day_duration = day_filtered.aggregate(Sum('duration')).get('duration__sum')

        day_distance_walk = day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
        day_distance_run = day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
        day_distance_bike = day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
        day_distance_ebike = day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

        if day_count is None:
            day_count = 0
        if day_duration is None:
            day_duration = timedelta(seconds=0)

        if day_distance_walk is None:
            day_distance_walk = 0
        if day_distance_run is None:
            day_distance_run = 0
        if day_distance_bike is None:
            day_distance_bike = 0
        if day_distance_ebike is None:
            day_distance_ebike = 0

        day_distance_score = score_of(day_distance_walk, day_distance_run, day_distance_bike, day_distance_ebike)

        # MONTH ##################################
        month_filtered = Run.objects.filter(creator=request.user.profile) \
            .filter(time_start__gte=datetime(year=today.year, month=today.month, day=1))

        month_count = month_filtered.count()
        month_duration = month_filtered.aggregate(Sum('duration')).get('duration__sum')

        month_distance_walk = month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
        month_distance_run = month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
        month_distance_bike = month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
        month_distance_ebike = month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
            'distance__sum')

        if month_count is None:
            month_count = 0
        if month_duration is None:
            month_duration = timedelta(seconds=0)

        if month_distance_walk is None:
            month_distance_walk = 0
        if month_distance_run is None:
            month_distance_run = 0
        if month_distance_bike is None:
            month_distance_bike = 0
        if month_distance_ebike is None:
            month_distance_ebike = 0

        month_distance_score = score_of(month_distance_walk, month_distance_run, month_distance_bike,
                                        month_distance_ebike)

        ########################################

        context.update({
            'user_stats_day': StatsRow(
                '% 6.0f' % day_distance_walk + ' km',
                '% 6.0f' % day_distance_run + ' km',
                '% 6.0f' % day_distance_bike + ' km',
                '% 6.0f' % day_distance_ebike + ' km',
                f'{day_count}',
                str(day_duration).split(':')[0] + " h",
                day_distance_score
            ),
            'user_stats_month': StatsRow(
                '% 6.0f' % month_distance_walk + ' km',
                '% 6.0f' % month_distance_run + ' km',
                '% 6.0f' % month_distance_bike + ' km',
                '% 6.0f' % month_distance_ebike + ' km',
                f'{month_count}',
                str(month_duration).split(':')[0] + " h",
                month_distance_score
            ),
        })

    notification_query = DashboardNotification.objects.filter(active=True, publish_by__lte=datetime.now()).order_by('pos_from_top')
    for noti in notification_query:
        if noti.close_by is None or noti.close_by > datetime.utcnow():
            print("notitype: ", noti.type)
            if noti.type == 0:
                messages.info(request, noti.msg)
            elif noti.type == 1:
                messages.warning(request, noti.msg)
            elif noti.type == 2:
                messages.error(request, noti.msg)
            elif noti.type == 3:
                messages.success(request, noti.msg)
            else:
                messages.info(request, noti.msg)

    return render(request, "dashboard/default/dashboard.html", context)


def community_view(request, *args, **kargs):
    today = datetime.today()

    # DAY ##################################
    day_filtered = Run.objects.filter(
        time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    day_count = day_filtered.count()
    day_duration = day_filtered.aggregate(Sum('duration')).get('duration__sum')

    day_distance_walk = day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    day_distance_run = day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    day_distance_bike = day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    day_distance_ebike = day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if day_count is None:
        day_count = 0
    if day_duration is None:
        day_duration = timedelta(seconds=0)

    if day_distance_walk is None:
        day_distance_walk = 0
    if day_distance_run is None:
        day_distance_run = 0
    if day_distance_bike is None:
        day_distance_bike = 0
    if day_distance_ebike is None:
        day_distance_ebike = 0

    day_distance_score = score_of(day_distance_walk, day_distance_run, day_distance_bike, day_distance_ebike)

    # WEEK ##################################
    week_filtered = Run.objects \
        .filter(
        time_start__gte=datetime.now() - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute))

    week_count = week_filtered.count()
    week_duration = week_filtered.aggregate(Sum('duration')).get('duration__sum')

    week_distance_walk = week_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    week_distance_run = week_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    week_distance_bike = week_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    week_distance_ebike = week_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if week_count is None:
        week_count = 0
    if week_duration is None:
        week_duration = timedelta(seconds=0)

    if week_distance_walk is None:
        week_distance_walk = 0
    if week_distance_run is None:
        week_distance_run = 0
    if week_distance_bike is None:
        week_distance_bike = 0
    if week_distance_ebike is None:
        week_distance_ebike = 0

    week_distance_score = score_of(week_distance_walk, week_distance_run, week_distance_bike, week_distance_ebike)

    # MONTH ##################################
    month_filtered = Run.objects.filter(time_start__gte=datetime(year=today.year, month=today.month, day=1))

    month_count = month_filtered.count()
    month_duration = month_filtered.aggregate(Sum('duration')).get('duration__sum')

    month_distance_walk = month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    month_distance_run = month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    month_distance_bike = month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    month_distance_ebike = month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if month_count is None:
        month_count = 0
    if month_duration is None:
        month_duration = timedelta(seconds=0)

    if month_distance_walk is None:
        month_distance_walk = 0
    if month_distance_run is None:
        month_distance_run = 0
    if month_distance_bike is None:
        month_distance_bike = 0
    if month_distance_ebike is None:
        month_distance_ebike = 0

    month_distance_score = score_of(month_distance_walk, month_distance_run, month_distance_bike, month_distance_ebike)

    # YEAR ##################################
    year_filtered = Run.objects.filter(time_start__gte=datetime(year=today.year, month=1, day=1))

    year_count = year_filtered.count()
    year_duration = year_filtered.aggregate(Sum('duration')).get('duration__sum')

    year_distance_walk = year_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    year_distance_run = year_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    year_distance_bike = year_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    year_distance_ebike = year_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if year_count is None:
        year_count = 0
    if year_duration is None:
        year_duration = timedelta(seconds=0)

    if year_distance_walk is None:
        year_distance_walk = 0
    if year_distance_run is None:
        year_distance_run = 0
    if year_distance_bike is None:
        year_distance_bike = 0
    if year_distance_ebike is None:
        year_distance_ebike = 0

    year_distance_score = score_of(year_distance_walk, year_distance_run, year_distance_bike, year_distance_ebike)

    ##################################################################################
    # Strava Data ####################################################################

    # DAY ##################################
    strava_day_filtered = StravaRun.objects.filter(
        time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    strava_day_count = strava_day_filtered.count()
    strava_day_duration = strava_day_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_day_distance_walk = strava_day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_run = strava_day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_bike = strava_day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_day_distance_ebike = strava_day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_day_count is None:
        strava_day_count = 0
    if strava_day_duration is None:
        strava_day_duration = timedelta(seconds=0)

    if strava_day_distance_walk is None:
        strava_day_distance_walk = 0
    if strava_day_distance_run is None:
        strava_day_distance_run = 0
    if strava_day_distance_bike is None:
        strava_day_distance_bike = 0
    if strava_day_distance_ebike is None:
        strava_day_distance_ebike = 0

    strava_day_distance_score = score_of(strava_day_distance_walk, strava_day_distance_run,
                                         strava_day_distance_bike, strava_day_distance_ebike)

    # WEEK ##################################
    strava_week_filtered = StravaRun.objects \
        .filter(
        time_start__gte=datetime.now() - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute))

    strava_week_count = strava_week_filtered.count()
    strava_week_duration = strava_week_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_week_distance_walk = strava_week_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_week_distance_run = strava_week_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_week_distance_bike = strava_week_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_week_distance_ebike = strava_week_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_week_count is None:
        strava_week_count = 0
    if strava_week_duration is None:
        strava_week_duration = timedelta(seconds=0)

    if strava_week_distance_walk is None:
        strava_week_distance_walk = 0
    if strava_week_distance_run is None:
        strava_week_distance_run = 0
    if strava_week_distance_bike is None:
        strava_week_distance_bike = 0
    if strava_week_distance_ebike is None:
        strava_week_distance_ebike = 0

    strava_week_distance_score = score_of(strava_week_distance_walk, strava_week_distance_run,
                                          strava_week_distance_bike, strava_week_distance_ebike)

    # MONTH ##################################
    strava_month_filtered = StravaRun.objects.filter(
        time_start__gte=datetime(year=today.year, month=today.month, day=1))

    strava_month_count = strava_month_filtered.count()
    strava_month_duration = strava_month_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_month_distance_walk = strava_month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_run = strava_month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_bike = strava_month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_month_distance_ebike = strava_month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_month_count is None:
        strava_month_count = 0
    if strava_month_duration is None:
        strava_month_duration = timedelta(seconds=0)

    if strava_month_distance_walk is None:
        strava_month_distance_walk = 0
    if strava_month_distance_run is None:
        strava_month_distance_run = 0
    if strava_month_distance_bike is None:
        strava_month_distance_bike = 0
    if strava_month_distance_ebike is None:
        strava_month_distance_ebike = 0

    strava_month_distance_score = score_of(strava_month_distance_walk, strava_month_distance_run,
                                           strava_month_distance_bike, strava_month_distance_ebike)

    # YEAR ##################################
    strava_year_filtered = StravaRun.objects.filter(time_start__gte=datetime(year=today.year, month=1, day=1))

    strava_year_count = strava_year_filtered.count()
    strava_year_duration = strava_year_filtered.aggregate(Sum('duration')).get('duration__sum')

    strava_year_distance_walk = strava_year_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_year_distance_run = strava_year_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_year_distance_bike = strava_year_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get(
        'distance__sum')
    strava_year_distance_ebike = strava_year_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get(
        'distance__sum')

    if strava_year_count is None:
        strava_year_count = 0
    if strava_year_duration is None:
        strava_year_duration = timedelta(seconds=0)

    if strava_year_distance_walk is None:
        strava_year_distance_walk = 0
    if strava_year_distance_run is None:
        strava_year_distance_run = 0
    if strava_year_distance_bike is None:
        strava_year_distance_bike = 0
    if strava_year_distance_ebike is None:
        strava_year_distance_ebike = 0

    strava_year_distance_score = score_of(strava_year_distance_walk, strava_year_distance_run,
                                          strava_year_distance_bike, strava_year_distance_ebike)

    ##################################################################################
    ##################################################################################

    community_month_score_sum = (month_distance_score + strava_month_distance_score)
    monthly_percentage = str(int((community_month_score_sum * 100.0 / goal_community_month)))

    context = {
        'community_stats_day': StatsRow(
            '% 6.0f' % (day_distance_walk + strava_day_distance_walk) + ' km',
            '% 6.0f' % (day_distance_run + strava_day_distance_run) + ' km',
            '% 6.0f' % (day_distance_bike + strava_day_distance_bike) + ' km',
            '% 6.0f' % (day_distance_ebike + strava_day_distance_ebike) + ' km',
            f'{(day_count + strava_day_count)}',
            str(day_duration + strava_day_duration).split(':')[0] + " h",
            (day_distance_score + strava_day_distance_score),
        ),
        'community_stats_week': StatsRow(
            '% 6.0f' % (week_distance_walk + strava_week_distance_walk) + ' km',
            '% 6.0f' % (week_distance_run + strava_week_distance_run) + ' km',
            '% 6.0f' % (week_distance_bike + strava_week_distance_bike) + ' km',
            '% 6.0f' % (week_distance_ebike + strava_week_distance_ebike) + ' km',
            f'{(week_count + strava_week_count)}',
            str(week_duration + strava_week_duration).split(':')[0] + " h",
            (week_distance_score + strava_week_distance_score),
        ),
        'stats_community_month_progressbar_text':
            monthly_percentage + " %" +
            " (" + str(int(community_month_score_sum)) + "/" + str(int(goal_community_month)) + " km)",
        'stats_community_month_progressbar_percent': monthly_percentage,
        'community_stats_month': StatsRow(
            '% 6.0f' % (month_distance_walk + strava_month_distance_walk) + ' km',
            '% 6.0f' % (month_distance_run + strava_month_distance_run) + ' km',
            '% 6.0f' % (month_distance_bike + strava_month_distance_bike) + ' km',
            '% 6.0f' % (month_distance_ebike + strava_month_distance_ebike) + ' km',
            f'{(month_count + strava_month_count)}',
            str(month_duration + strava_month_duration).split(':')[0] + " h",
            (month_distance_score + strava_month_distance_score),
        ),
        'community_stats_year': StatsRow(
            '% 6.0f' % (year_distance_walk + strava_year_distance_walk) + ' km',
            '% 6.0f' % (year_distance_run + strava_year_distance_run) + ' km',
            '% 6.0f' % (year_distance_bike + strava_year_distance_bike) + ' km',
            '% 6.0f' % (year_distance_ebike + strava_year_distance_ebike) + ' km',
            f'{(year_count + strava_year_count)}',
            str(year_duration + strava_year_duration).split(':')[0] + " h",
            (year_distance_score + strava_year_distance_score),
        ),
    }

    return render(request, "dashboard/community/dashboard.html", context)


@login_required
def user_view(request, *args, **kargs):
    today = datetime.today()

    # DAY ##################################
    day_filtered = Run.objects.filter(creator=request.user.profile) \
        .filter(time_start__gte=datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    print("day_start: ", datetime.now() - timedelta(hours=today.hour, minutes=today.minute))

    day_count = day_filtered.count()
    day_duration = day_filtered.aggregate(Sum('duration')).get('duration__sum')

    day_distance_walk = day_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    day_distance_run = day_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    day_distance_bike = day_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    day_distance_ebike = day_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if day_count is None:
        day_count = 0
    if day_duration is None:
        day_duration = timedelta(seconds=0)

    if day_distance_walk is None:
        day_distance_walk = 0
    if day_distance_run is None:
        day_distance_run = 0
    if day_distance_bike is None:
        day_distance_bike = 0
    if day_distance_ebike is None:
        day_distance_ebike = 0

    day_distance_score = score_of(day_distance_walk, day_distance_run, day_distance_bike, day_distance_ebike)

    # WEEK ##################################
    week_filtered = Run.objects.filter(creator=request.user.profile) \
        .filter(
        time_start__gte=datetime.now() - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute))

    print("week_start: ", datetime.now() - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute))

    week_count = week_filtered.count()
    week_duration = week_filtered.aggregate(Sum('duration')).get('duration__sum')

    week_distance_walk = week_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    week_distance_run = week_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    week_distance_bike = week_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    week_distance_ebike = week_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if week_count is None:
        week_count = 0
    if week_duration is None:
        week_duration = timedelta(seconds=0)

    if week_distance_walk is None:
        week_distance_walk = 0
    if week_distance_run is None:
        week_distance_run = 0
    if week_distance_bike is None:
        week_distance_bike = 0
    if week_distance_ebike is None:
        week_distance_ebike = 0

    week_distance_score = score_of(week_distance_walk, week_distance_run, week_distance_bike, week_distance_ebike)

    # MONTH ##################################
    month_filtered = Run.objects.filter(creator=request.user.profile) \
        .filter(time_start__gte=datetime(year=today.year, month=today.month, day=1))

    month_count = month_filtered.count()
    month_duration = month_filtered.aggregate(Sum('duration')).get('duration__sum')

    month_distance_walk = month_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    month_distance_run = month_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    month_distance_bike = month_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    month_distance_ebike = month_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if month_count is None:
        month_count = 0
    if month_duration is None:
        month_duration = timedelta(seconds=0)

    if month_distance_walk is None:
        month_distance_walk = 0
    if month_distance_run is None:
        month_distance_run = 0
    if month_distance_bike is None:
        month_distance_bike = 0
    if month_distance_ebike is None:
        month_distance_ebike = 0

    month_distance_score = score_of(month_distance_walk, month_distance_run, month_distance_bike, month_distance_ebike)

    # YEAR ##################################
    year_filtered = Run.objects.filter(creator=request.user.profile) \
        .filter(time_start__gte=datetime(year=today.year, month=1, day=1))

    year_count = year_filtered.count()
    year_duration = year_filtered.aggregate(Sum('duration')).get('duration__sum')

    year_distance_walk = year_filtered.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
    year_distance_run = year_filtered.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
    year_distance_bike = year_filtered.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
    year_distance_ebike = year_filtered.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')

    if year_count is None:
        year_count = 0
    if year_duration is None:
        year_duration = timedelta(seconds=0)

    if year_distance_walk is None:
        year_distance_walk = 0
    if year_distance_run is None:
        year_distance_run = 0
    if year_distance_bike is None:
        year_distance_bike = 0
    if year_distance_ebike is None:
        year_distance_ebike = 0

    year_distance_score = score_of(year_distance_walk, year_distance_run, year_distance_bike, year_distance_ebike)

    ########################################

    context = {
        'user_stats_day': StatsRow(
            '% 6.0f' % day_distance_walk + ' km',
            '% 6.0f' % day_distance_run + ' km',
            '% 6.0f' % day_distance_bike + ' km',
            '% 6.0f' % day_distance_ebike + ' km',
            f'{day_count}',
            str(day_duration).split(':')[0] + " h",
            day_distance_score
        ),
        'user_stats_week': StatsRow(
            '% 6.0f' % week_distance_walk + ' km',
            '% 6.0f' % week_distance_run + ' km',
            '% 6.0f' % week_distance_bike + ' km',
            '% 6.0f' % week_distance_ebike + ' km',
            f'{week_count}',
            str(week_duration).split(':')[0] + " h",
            week_distance_score
        ),
        'user_stats_month': StatsRow(
            '% 6.0f' % month_distance_walk + ' km',
            '% 6.0f' % month_distance_run + ' km',
            '% 6.0f' % month_distance_bike + ' km',
            '% 6.0f' % month_distance_ebike + ' km',
            f'{month_count}',
            str(month_duration).split(':')[0] + " h",
            month_distance_score
        ),
        'user_stats_year': StatsRow(
            '% 6.0f' % year_distance_walk + ' km',
            '% 6.0f' % year_distance_run + ' km',
            '% 6.0f' % year_distance_bike + ' km',
            '% 6.0f' % year_distance_ebike + ' km',
            f'{year_count}',
            str(year_duration).split(':')[0] + " h",
            year_distance_score
        ),
    }

    return render(request, "dashboard/user/dashboard.html", context)
