from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from group.models import Group
from group.score_updater import score_update
from route.models import Route
from run.models import Run


def _get_run_dict(
        run_id,
        creator_id,
        route_id,
        distance,
        elevation_gain,
        type,
        time_start,
        duration,
        note,
        group_id,
    ):
    dic = {
        "id": run_id,
        "creator_id": creator_id,
        "distance": distance,
        "elevation_gain": elevation_gain,
        "type": str(type),
        "time_start": str(time_start),
        "duration": str(duration),
    }

    if route_id:
        dic.update({"route_id": route_id,})

    if note:
        dic.update({"note": note,})

    if group_id:
        dic.update({"group_id": group_id,})

    return dic


def _get_run_dict_from_obj(run: Run):
    return _get_run_dict(
        run.id,
        run.creator_id,
        run.route_id,
        run.distance,
        run.elevation_gain,
        str(run.type),
        str(run.time_start),
        str(run.duration),
        run.note,
        run.group_id,
    )


def _get_example_run():
    return _get_run_dict(
        343,
        4,
        2,
        13.764,
        1234,
        "RUN",
        "2021-04-01 12:45:00.000000",
        6339000000,
        "TEST123 123 test",
        3
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request, *args, **kwargs):
    context = {
        'code': '200',
        'status': 'success',
        'detail': 'token is working fine!'
    }
    return JsonResponse(context, status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_id(request, *args, **kwargs):
    context = {
        'user_id': request.user.id,
        'profile_id': request.user.profile.id,
    }
    return JsonResponse(context, status=200)


# +++++++++++++++++++++++++++++++++++++++++++

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def run_detail(request, run_id, *args, **kwargs):
    form_error = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_run ====================================

    exists = Run.objects.filter(id=run_id).exists()
    if not exists:
        form_error.update({
            'code': '404',
            'detail': 'This run does not exist!'
        })
        return JsonResponse(form_error, status=404)

    run = Run.objects.get(id=run_id)

    # ACCESS CONTROL ##############
    if not run.group:  # runs for groups are public by design
        if run.creator.user.id != request.user.id:
            form_error.update({
                'code': '401',
                'detail': 'Insufficient rights!'
            })
            return JsonResponse(form_error, status=401)

    # ================================================

    object = _get_run_dict_from_obj(run)

    return JsonResponse(data=object, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def run_create(request, *args, **kwargs):
    read_route_id = request.POST.get("route_id")
    read_distance = request.POST.get("distance")
    read_elevation_gain = request.POST.get("elevation_gain")
    read_type = request.POST.get("type")
    read_time_start = request.POST.get("time_start")
    read_duration = request.POST.get("duration")
    read_group_id = request.POST.get("group_id")
    read_note = request.POST.get("note")

    route_id = None
    distance = None
    elevation_gain = None
    type = None
    time_start = None
    duration = None
    group_id = None
    note = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_route ====================================

    if not read_route_id:
        route = None

    else:
        read_route_id = int(read_route_id)

        exists = Route.objects.filter(id=read_route_id).exists()

        if exists:
            route = Route.objects.get(id=read_route_id)
        else:
            response_object.update({
                'code': '400-1',
                'detail': 'This route does not exist!'
            })
            return JsonResponse(response_object, status=400)

    # ================================================
    # clean_distance ===============================

    if read_distance:
        read_distance = float(read_distance)

    if route:
        distance = route.distance

    else:
        if read_distance is None:
            response_object.update({
                'code': '400-2',
                'detail': 'If no route is selected, distance must not be null!'
            })
            return JsonResponse(response_object, status=400)

        if read_distance > 5000.0:
            response_object.update({
                'code': '400-3',
                'detail': 'Activities over 5000 km are not allowed!'
            })
            return JsonResponse(response_object, status=400)

        if read_distance <= 0:
            response_object.update({
                'code': '400-4',
                'detail': 'Distance must be longer than 0.0 km!'
            })
            return JsonResponse(response_object, status=400)

        distance = float(read_distance)

    # ================================================
    # clean_elevation_gain ===========================

    if read_elevation_gain:
        read_elevation_gain = float(read_elevation_gain)

    if route:
        elevation_gain = route.elevation_gain

    else:
        if read_elevation_gain is None:
            elevation_gain = 0.0

        else:
            if read_elevation_gain > 10000.0:
                response_object.update({
                    'code': '400-5',
                    'detail': 'Activities over 10000 meters elevation gain are not allowed!'
                })
                return JsonResponse(response_object, status=400)

            if read_elevation_gain < 0:
                response_object.update({
                    'code': '400-6',
                    'detail': 'Elevation-gain must not be negative!'
                })
                return JsonResponse(response_object, status=400)

            elevation_gain = read_elevation_gain

    # ================================================
    # clean_type ===============================

    if read_type is None:
        response_object.update({
            'code': '400-7',
            'detail': 'Activity type needs to be specified!'
        })
        return JsonResponse(response_object, status=400)

    if str(read_type).upper() == Run.TYPE_WALK \
            or str(read_type).upper() == Run.TYPE_RUN \
            or str(read_type).upper() == Run.TYPE_BIKE \
            or str(read_type).upper() == Run.TYPE_EBIKE:
        type = str(read_type).upper()

    else:
        response_object.update({
            'code': '400-8',
            'detail': 'Activity type must be one of the following: { WALK, RUN, BIKE, E-BIKE }!'
        })
        return JsonResponse(response_object, status=400)

    # ================================================
    # clean_time_start ===============================

    if read_time_start is None:
        time_start = datetime.now().strftime("%Y-%m-%d %H:%M")

    else:
        read_time_start = datetime.fromisoformat(read_time_start)
        today = datetime.now().replace(tzinfo=None)
        one_week = timedelta(weeks=1)
        time_start = read_time_start.replace(tzinfo=None)

        delta = today - read_time_start

        if delta > one_week:
            response_object.update({
                'code': '400-9',
                'detail': "Run's start time mustn't lie back more than 7 days!"
            })
            return JsonResponse(response_object, status=400)

        # if read_time > today:
        #     response_object.update({
        #         'code': '400-10',
        #         'detail': "Run's start time mustn't lie in the future!"
        #     })
        #     return JsonResponse(form_error, status=400)

    # ================================================
    # clean_duration ===============================

    if read_duration is None:
        response_object.update({
            'code': '400-11',
            'detail': 'Duration must not be empty!'
        })
        return JsonResponse(response_object, status=400)
    else:
        read_duration = int(read_duration)
        duration = timedelta(microseconds=read_duration)

    # ================================================
    # clean_group ====================================

    if not read_group_id:
        group = None

    else:
        read_group_id = int(read_group_id)

        exists = Group.objects.filter(id=read_group_id).exists()

        if exists:
            group = Group.objects.get(id=read_group_id)

        else:
            response_object.update({
                'code': '400-12',
                'detail': 'This group does not exist!'
            })
            return JsonResponse(response_object, status=400)

    # ================================================
    # clean_note ===============================

    if read_note and len(str(read_note)) > 0:
        note = str(read_note)

    # ================================================

    instance = Run.objects.create(
        creator=request.user.profile,

        distance=distance,
        elevation_gain=elevation_gain,
        route=route,

        time_start=time_start,
        duration=duration,
        group=group,

        type=type,

        note=note
    )

    score_update()

    response_object = {
        'code': '201',
        'status': 'successful',
        'id': instance.id,
    }

    return JsonResponse(response_object, status=201)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def run_edit(request, run_id, *args, **kwargs):
    read_route_id = request.POST.get("route_id")
    read_distance = request.POST.get("distance")
    read_elevation_gain = request.POST.get("elevation_gain")
    read_type = request.POST.get("type")
    read_time_start = request.POST.get("time_start")
    read_duration = request.POST.get("duration")
    read_group_id = request.POST.get("group_id")
    read_note = request.POST.get("note")

    route_id = None
    distance = None
    elevation_gain = None
    type = None
    time_start = None
    duration = None
    group_id = None
    note = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_run ======================================

    exists = Run.objects.filter(id=run_id).exists()
    if not exists:
        response_object.update({
            'code': '404',
            'detail': 'This run does not exist!'
        })
        return JsonResponse(response_object, status=404)

    run = Run.objects.get(id=run_id)

    # ACCESS CONTROL ##############
    if run.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================
    # clean_route ====================================

    if read_route_id is None:
        route = None

    else:
        read_route_id = int(read_route_id)

        exists = Route.objects.filter(id=read_route_id).exists()

        if exists:
            route = Route.objects.get(id=read_route_id)
        else:
            response_object.update({
                'code': '400-1',
                'detail': 'This route does not exist!'
            })
            return JsonResponse(response_object, status=400)

    # ================================================
    # clean_distance ===============================

    if read_distance:
        read_distance = float(read_distance)

    if route:
        distance = route.distance

    else:
        if read_distance is None:
            response_object.update({
                'code': '400-2',
                'detail': 'If no route is selected, distance must not be null!'
            })
            return JsonResponse(response_object, status=400)

        if read_distance > 5000.0:
            response_object.update({
                'code': '400-3',
                'detail': 'Activities over 5000 km are not allowed!'
            })
            return JsonResponse(response_object, status=400)

        if read_distance <= 0:
            response_object.update({
                'code': '400-4',
                'detail': 'Distance must be longer than 0.0 km!'
            })
            return JsonResponse(response_object, status=400)

        distance = float(read_distance)

    # ================================================
    # clean_elevation_gain ===========================

    if read_elevation_gain:
        read_elevation_gain = float(read_elevation_gain)

    if route:
        elevation_gain = route.elevation_gain

    else:
        if read_elevation_gain is None:
            elevation_gain = 0.0

        else:
            if read_elevation_gain > 10000.0:
                response_object.update({
                    'code': '400-5',
                    'detail': 'Activities over 10000 meters elevation gain are not allowed!'
                })
                return JsonResponse(response_object, status=400)

            if read_elevation_gain < 0:
                response_object.update({
                    'code': '400-6',
                    'detail': 'Elevation-gain must not be negative!'
                })
                return JsonResponse(response_object, status=400)

            elevation_gain = read_elevation_gain

    # ================================================
    # clean_type =====================================

    if read_type is None:
        response_object.update({
            'code': '400-7',
            'detail': 'Activity type needs to be specified!'
        })
        return JsonResponse(response_object, status=400)

    if str(read_type).upper() == Run.TYPE_WALK \
            or str(read_type).upper() == Run.TYPE_RUN \
            or str(read_type).upper() == Run.TYPE_BIKE \
            or str(read_type).upper() == Run.TYPE_EBIKE:
        type = str(read_type).upper()

    else:
        response_object.update({
            'code': '400-8',
            'detail': 'Activity type must be one of the following: { WALK, RUN, BIKE, E-BIKE }!'
        })
        return JsonResponse(response_object, status=400)

    # ================================================
    # clean_time_start ===============================

    if read_time_start is None:
        time_start = datetime.now().strftime("%Y-%m-%d %H:%M")

    else:
        read_time_start = datetime.fromisoformat(read_time_start)
        today = datetime.now().replace(tzinfo=None)
        one_week = timedelta(weeks=1)
        time_start = read_time_start.replace(tzinfo=None)

        delta = today - read_time_start

        if delta > one_week:
            response_object.update({
                'code': '400-9',
                'detail': "Run's start time mustn't lie back more than 7 days!"
            })
            return JsonResponse(response_object, status=400)

        # if read_time > today:
        #     response_object.update({
        #         'code': '400-10',
        #         'detail': "Run's start time mustn't lie in the future!"
        #     })
        #     return JsonResponse(response_object, status=400)

    # ================================================
    # clean_duration ===============================

    if read_duration is None:
        response_object.update({
            'code': '400-11',
            'detail': 'Duration must not be empty!'
        })
        return JsonResponse(response_object, status=400)
    else:
        read_duration = int(read_duration)
        duration = timedelta(microseconds=read_duration)

    # ================================================
    # clean_group ====================================

    if read_group_id is None:
        group = None

    else:
        read_group_id = int(read_group_id)

        exists = Group.objects.filter(id=read_group_id).exists()

        if exists:
            group = Group.objects.get(id=read_group_id)

        else:
            response_object.update({
                'code': '400-12',
                'detail': 'This group does not exist!'
            })
            return JsonResponse(response_object, status=400)

    # ================================================
    # clean_note ===============================

    if read_note and len(str(read_note)) > 0:
        note = str(read_note)

    # ================================================

    run.creator = request.user.profile

    run.distance = distance

    run.elevation_gain = elevation_gain
    run.route = route

    run.time_start = time_start
    run.duration = duration
    run.group = group

    run.type = type
    run.note = note
    run.save()

    score_update()

    response_object = {
        'code': '200',
        'status': 'successful',
        'id': run.id,
    }
    return JsonResponse(response_object, status=200)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def run_delete(request, run_id, *args, **kwargs):

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_run ======================================

    exists = Run.objects.filter(id=run_id).exists()
    if not exists:
        response_object.update({
            'code': '404',
            'detail': 'This run does not exist!'
        })
        return JsonResponse(response_object, status=404)

    run = Run.objects.get(id=run_id)

    # ACCESS CONTROL ##############
    if run.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================

    run.delete()

    score_update()

    response_object = {
        'code': '200',
        'status': 'successful',
    }
    return JsonResponse(response_object, status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def run_list_user(request, *args, **kwargs):
    runs = Run.objects.filter(creator=request.user.profile)
    object_list = []

    for run in runs:
        object_list.append(_get_run_dict_from_obj(run))

    return JsonResponse(object_list, safe=False, status=200)
