from datetime import date, datetime, time, timedelta

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.messages.views import messages

from django.core.paginator import Paginator

from dashboard.views import StatsRow
from .forms import GroupCreateForm
from .models import Group
from run.models import Run
from user.models import Profile
from .score_updater import score_of, read_strava_data
from run.models import StravaRun


def _user_get_num_groups(user):
    return Group.objects.filter(creator=user.profile).count()


def _user_get_max_groups(user):
    profile_role = user.profile.role

    if profile_role == Profile.ROLE_ADMIN:
        return 2000
    elif profile_role == Profile.ROLE_HEAD_TRAINER:
        return 50
    elif profile_role == Profile.ROLE_TRAINER:
        return 10
    else:
        return 0  # Profile.ROLE_USER


def _user_can_create_group_u(user):
    num = _user_get_num_groups(user)
    max_num = _user_get_max_groups(user)
    return _user_can_create_group(num, max_num)


def _user_can_create_group(num, max_num):
    return num < max_num


def _user_get_filtered_groups(user):
    groups = Group.objects.filter(creator=user.profile)
    groups.order_by('score')
    return groups


def _get_strava_group_stats():
    strava_stats = read_strava_data()
    return StravaGroupStats(
        group_num_participants=strava_stats.num_participants,
        group_score=strava_stats.score_value,
        group_distance=strava_stats.sum_distance_run  # TODO more types
    )


def _get_strava_group_user_stats_list():
    runners = []

    group_users = StravaRun.objects.all().group_by('creator').distinct()

    for obj in group_users:
        group_user_runs = StravaRun.objects.filter(creator=obj.creator)

        group_count = group_user_runs.count()
        if group_count is None:
            group_count = 0

        group_duration = group_user_runs.aggregate(Sum('duration')).get('duration__sum')
        if group_duration is None:
            group_duration = timedelta(seconds=0)

        group_distance_walk = 0

        group_distance_run = group_user_runs.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
        if group_distance_run is None:
            group_distance_run = 0

        group_distance_bike = 0
        group_distance_ebike = 0

        runners.append(_get_strava_group_user_stats_item(
            obj.creator,
            group_count,

            group_distance_walk, group_distance_run,
            group_distance_bike, group_distance_ebike,

            int(group_duration.seconds) / 3600
        ))

    return runners


def dashboard_forward(request, *args, **kargs):
    return redirect("/group/list/")
    # return redirect("/group/dashboard/")


def dashboard_view(request, *args, **kargs):
    return redirect("/group/list/")
    # return render(request, "root.html", {})


def help_view(request, *args, **kargs):
    if request.user.is_authenticated:
        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
        }
    else:
        context = {}

    return render(request, "group/group_score_help.html", context)


class StravaGroupStats:

    def __init__(self, group_num_participants, group_distance, group_score):
        self.group_num_participants = group_num_participants
        self.group_distance = group_distance
        self.group_score = group_score


ERROR_MAX_GROUP_NUMBER_REACHED = "Sie können keine Gruppe mehr erstellen, da Sie bereits Ihr maximales Kontingent " \
                                 "aufgebraucht haben! Wir haben Sie deshalb zur Übersicht Ihrer Gruppen weitergeleitet!"

ERROR_GROUP_NOT_EXISTING_FORWARD_LIST = "Diese Gruppe existiert nicht! Wir haben Sie deshalb zu Ihrer Gruppenliste weitergeleitet!"
ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE = "Diese Gruppe existiert nicht! Hier können Sie eine neue anlegen!"
ERROR_NO_ACCESS_TO_GROUP = "Sie haben auf diese Gruppe keinen Zugriff! Wir haben Sie deshalb zu Ihrer Laufliste weitergeleitet!"


class GroupDetailView(View):
    template_name = 'group/group_detail.html'

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")
        ################################

        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
            'group': group,
        }

        return render(request, self.template_name, context)


class GroupCreateView(CreateView):
    template_name = 'group/group_create.html'

    def get(self, request, *args, **kwargs):
        if not _user_can_create_group_u(request.user):
            messages.error(request, ERROR_MAX_GROUP_NUMBER_REACHED)
            return redirect("group/list-user/")

        form = GroupCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if not _user_can_create_group_u(request.user):
            messages.error(request, ERROR_MAX_GROUP_NUMBER_REACHED)
            return redirect("group/list-user/")

        form = GroupCreateForm(request.POST)
        if form.is_valid() and request.user:
            group = form.create_new(request.user)
            if group:
                return redirect("/group/detail/" + str(group.id))
            else:
                form = GroupCreateForm(request.user)
        return render(request, self.template_name, {'form': form})


class GroupUpdateView(View):
    template_name = 'group/group_update.html'

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")

        # ACCESS CONTROL ##############
        if group.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_GROUP)
            return redirect("/group/list-user/")
        ###############################

        init = {
            'name': group.name,
            'description': group.description,
        }
        form = GroupCreateForm(initial=init)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = GroupCreateForm(request.POST)
        group_id = self.kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/group/create/")

        # ACCESS CONTROL ##############
        if group.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_GROUP)
            return redirect("/group/list-user/")
        ###############################

        if form.is_valid() and request.user:
            group = form.save_existing(request.user, group)
            if group:
                return redirect("/group/detail/" + str(group.id))
            else:
                form = GroupCreateForm(user=request.user)
        return render(request, self.template_name, {'form': form})


class GroupDeleteView(DeleteView):
    template_name = 'group/group_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/create/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/create/")

        # ACCESS CONTROL ##############
        if group.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_GROUP)
            return redirect("/group/list-user/")
        ###############################

        context = {
            'group': group
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = GroupCreateForm(request.POST)
        group_id = kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/create/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/create/")

        # ACCESS CONTROL ##############
        if group.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_GROUP)
            return redirect("/group/list-user/")
        ###############################

        group.delete()
        messages.success(request, "Gruppe erfolgreich gelöscht!")

        return redirect("/group/list-user/")


class GroupListView(View):
    template_name = "group/group_list.html"

    def get(self, request, *args, **kwargs):
        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)
        groups = Group.objects.all().order_by('score')

        paginator = Paginator(groups, 10)
        page = request.GET.get('page')

        strava_stats = _get_strava_group_stats()

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
            'page_obj': paginator.page(page or 1),

            'strava_participants_num': strava_stats.group_num_participants,
            'strava_distance_run': strava_stats.group_distance,
            'strava_score': strava_stats.group_score,
        }

        return render(request, self.template_name, context)


class GroupListUserView(View):
    template_name = "group/group_list_user.html"

    def get(self, request, *args, **kwargs):
        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)
        queryset = _user_get_filtered_groups(request.user).order_by('score')

        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
            'page_obj': paginator.page(page or 1)
        }

        return render(request, self.template_name, context)


class GroupStatsView(View):
    template_name = 'group/group_stats.html'

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')

        ################################
        exists = Group.objects.filter(id=group_id).exists()
        if not exists:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/list-user/")

        group = Group.objects.get(id=group_id)

        if group is None:
            messages.error(request, ERROR_GROUP_NOT_EXISTING_FORWARD_LIST)
            return redirect("/group/list-user/")
        ################################

        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
            'group': group,
        }
        ################################
        tab = request.GET.get('tab')
        if tab is None:
            tab = 'runners'

        context.update({'tab': tab})

        if tab == 'runners':
            object_list = _get_group_user_stats_list(group)

            sort = request.GET.get('sort')
            if sort is None:
                sort = 'count'

            context.update({'sort': sort})

            if sort == 'count':
                object_list.sort(key=get_runs, reverse=True)
            elif sort == 'duration':
                object_list.sort(key=get_duration, reverse=True)
            elif sort == 'alphabet':
                object_list.sort(key=get_name)
            elif sort == 'distance':
                object_list.sort(key=get_distance, reverse=True)
            else:  # score
                object_list.sort(key=get_score, reverse=True)

            paginator = Paginator(object_list, 16)
            page = request.GET.get('page')

            context.update({
                'page_obj': paginator.page(page or 1)
            })

        elif tab == 'runs':
            object_list = _get_group_runs_stats_list(group)

            sort = request.GET.get('sort')
            if sort is None:
                sort = 'time'

            context.update({'sort': sort})

            if sort == 'time':
                object_list.sort(key=get_time, reverse=True)
            elif sort == 'duration':
                object_list.sort(key=get_duration, reverse=True)
            elif sort == 'distance':
                object_list.sort(key=get_distance, reverse=True)
            else:  # score
                object_list.sort(key=get_score, reverse=True)

            paginator = Paginator(object_list, 16)
            page = request.GET.get('page')

            context.update({
                'page_obj': paginator.page(page or 1)
            })

        else:  # stats
            return _group_stats_view_helper(request, self.template_name, group, context)

        return render(request, self.template_name, context)


class StravaGroupStatsView(View):
    template_name = 'group/strava_group_stats.html'

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')

        num = _user_get_num_groups(request.user)
        max_num = _user_get_max_groups(request.user)
        can_create = _user_can_create_group(num, max_num)

        context = {
            'group_counter': num,
            'group_max_counter': max_num,
            'group_can_create': can_create,
        }
        ################################
        tab = request.GET.get('tab')
        if tab is None:
            tab = 'runners'

        context.update({'tab': tab})

        if tab == 'runners':
            object_list = _get_strava_group_user_stats_list()

            sort = request.GET.get('sort')
            if sort is None:
                sort = 'count'

            context.update({'sort': sort})

            if sort == 'count':
                object_list.sort(key=get_runs, reverse=True)
            elif sort == 'duration':
                object_list.sort(key=get_duration, reverse=True)
            elif sort == 'alphabet':
                object_list.sort(key=get_name)
            elif sort == 'distance':
                object_list.sort(key=get_distance, reverse=True)
            else:  # score
                object_list.sort(key=get_score, reverse=True)

            paginator = Paginator(object_list, 16)
            page = request.GET.get('page')

            context.update({
                'page_obj': paginator.page(page or 1)
            })

            return render(request, self.template_name, context)

        elif tab == 'runs':
            return redirect("/strava-run/list/")

        else:  # stats
            return redirect("/group/strava-stats")


def _group_stats_view_helper(request, template, group, context):
    today = datetime.today()

    # DAY ##################################
    day_filtered = Run.objects.filter(group=group) \
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

    # WEEK ##################################
    week_filtered = Run.objects.filter(group=group) \
        .filter(time_start__gte=datetime.now() - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute))

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
    month_filtered = Run.objects.filter(group=group) \
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
    year_filtered = Run.objects.filter(group=group) \
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

    context.update(
        {
            'group_stats_day': StatsRow(
                '% 6.0f' % day_distance_walk + ' km',
                '% 6.0f' % day_distance_run + ' km',
                '% 6.0f' % day_distance_bike + ' km',
                '% 6.0f' % day_distance_ebike + ' km',
                f'{day_count}',
                str(day_duration).split(':')[0] + " h",
                day_distance_score
            ),
            'group_stats_week': StatsRow(
                '% 6.0f' % week_distance_walk + ' km',
                '% 6.0f' % week_distance_run + ' km',
                '% 6.0f' % week_distance_bike + ' km',
                '% 6.0f' % week_distance_ebike + ' km',
                f'{week_count}',
                str(week_duration).split(':')[0] + " h",
                week_distance_score
            ),
            'group_stats_month': StatsRow(
                '% 6.0f' % month_distance_walk + ' km',
                '% 6.0f' % month_distance_run + ' km',
                '% 6.0f' % month_distance_bike + ' km',
                '% 6.0f' % month_distance_ebike + ' km',
                f'{month_count}',
                str(month_duration).split(':')[0] + " h",
                month_distance_score
            ),
            'group_stats_year': StatsRow(
                '% 6.0f' % year_distance_walk + ' km',
                '% 6.0f' % year_distance_run + ' km',
                '% 6.0f' % year_distance_bike + ' km',
                '% 6.0f' % year_distance_ebike + ' km',
                f'{year_count}',
                str(year_duration).split(':')[0] + " h",
                year_distance_score
            ),
        }
    )

    return render(request, template, context)


def _get_group_user_stats_list(group):
    object_list = []
    group_user = Run.objects.filter(group=group).group_by('creator').distinct()

    for obj in group_user:
        group_user_runs = Run.objects.filter(group=group, creator=obj.creator)

        group_count = group_user_runs.count()
        if group_count is None:
            group_count = 0

        group_duration = group_user_runs.aggregate(Sum('duration')).get('duration__sum')
        if group_duration is None:
            group_duration = timedelta(seconds=0)

        group_distance_walk = group_user_runs.filter(type=Run.TYPE_WALK).aggregate(Sum('distance')).get('distance__sum')
        if group_distance_walk is None:
            group_distance_walk = 0

        group_distance_run = group_user_runs.filter(type=Run.TYPE_RUN).aggregate(Sum('distance')).get('distance__sum')
        if group_distance_run is None:
            group_distance_run = 0

        group_distance_bike = group_user_runs.filter(type=Run.TYPE_BIKE).aggregate(Sum('distance')).get('distance__sum')
        if group_distance_bike is None:
            group_distance_bike = 0

        group_distance_ebike = group_user_runs.filter(type=Run.TYPE_EBIKE).aggregate(Sum('distance')).get('distance__sum')
        if group_distance_ebike is None:
            group_distance_ebike = 0

        object_list.append(_get_group_user_stats_item(
            obj.creator.user.username,
            obj.creator.name,
            group_count,

            group_distance_walk, group_distance_run,
            group_distance_bike, group_distance_ebike,

            int(group_duration.seconds) / 3600
        ))

    return object_list


def _get_group_runs_stats_list(group):
    object_list = []
    queried = Run.objects.filter(group=group)

    for obj in queried:

        group_distance_walk = 0
        group_distance_run = 0
        group_distance_bike = 0
        group_distance_ebike = 0

        if obj.type == Run.TYPE_WALK:
            group_distance_walk = obj.distance
        elif obj.type == Run.TYPE_BIKE:
            group_distance_bike = obj.distance
        elif obj.type == Run.TYPE_EBIKE:
            group_distance_ebike = obj.distance
        else:  # Run.TYPE_RUN
            group_distance_run = obj.distance

        object_list.append(
            _get_group_runs_stats_item(
                obj.creator.user.username,
                obj.creator.name,
                obj.type,
                obj.time_start,

                group_distance_walk,
                group_distance_run,
                group_distance_bike,
                group_distance_ebike,

                int(obj.duration.seconds) / 3600,
            )
        )

    return object_list


def get_name(item):
    return item.get('name')


def get_time(item):
    return item.get('time_start')


def get_runs(item):
    return item.get('runs')


def get_distance(item):
    return item.get('distance')


def get_score(item):
    return item.get('score')


def get_duration(item):
    return item.get('duration')


def _get_group_user_stats_item(username, name, runs,
                               distance_walk, distance_run,
                               distance_bike, distance_ebike,
                               duration):
    return {
        'username': username,
        'name': name,

        'runs': runs,
        'duration': duration,

        'distance': distance_walk + distance_run + distance_bike + distance_ebike,
        'distance_walk': distance_walk,
        'distance_run': distance_run,
        'distance_bike': distance_bike,
        'distance_ebike': distance_ebike,

        'score': score_of(distance_walk, distance_run, distance_bike, distance_ebike)
    }


def _get_group_runs_stats_item(username, name,
                               run_type, time_start,
                               distance_walk, distance_run,
                               distance_bike, distance_ebike,
                               duration):
    return {
        'username': username,
        'name': name,
        'type': run_type,

        'time_start': time_start,
        'duration': duration,

        'distance': distance_walk + distance_run + distance_bike + distance_ebike,
        'distance_walk': distance_walk,
        'distance_run': distance_run,
        'distance_bike': distance_bike,
        'distance_ebike': distance_ebike,

        'score': score_of(distance_walk, distance_run, distance_bike, distance_ebike)
    }


def _get_strava_group_user_stats_item(creator, runs,
                               distance_walk, distance_run,
                               distance_bike, distance_ebike,
                               duration):
    return {
        'name': creator,

        'runs': runs,
        'duration': duration,  # in hours

        'distance': distance_walk + distance_run + distance_bike + distance_ebike,
        'distance_walk': distance_walk,
        'distance_run': distance_run,
        'distance_bike': distance_bike,
        'distance_ebike': distance_ebike,

        'score': score_of(distance_walk, distance_run, distance_bike, distance_ebike)
    }
