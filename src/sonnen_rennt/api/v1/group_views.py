
import json

from django.http import HttpResponse, JsonResponse

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from group.models import Group


def _get_group_dict(
        id, creator_id, name, description,

        score, run_count, num_participants,

        sum_duration,

        sum_distance_walk,
        sum_distance_run,
        sum_distance_bike,
        sum_distance_ebike
    ):

    dic = {
        "id": id,
        "creator_id": creator_id,
        "name": name,

        "score": score,
        "run_count": run_count,
        "num_participants": num_participants,

        "sum_duration": sum_duration,

        "sum_distance_walk": sum_distance_walk,
        "sum_distance_run": sum_distance_run,
        "sum_distance_bike": sum_distance_bike,
        "sum_distance_ebike": sum_distance_ebike,
    }

    if description:
        dic.update({"description": description})

    return dic


def _get_group_dict_from_obj(group):
    return {
        "id": group.id,
        "creator_id": group.creator_id,
        "name": group.name,
        "description": group.description,

        "score": group.score,
        "run_count": group.run_count,
        "num_participants": group.num_participants,

        "sum_duration": group.sum_duration,

        "sum_distance_walk": group.sum_distance_walk,
        "sum_distance_run": group.sum_distance_run,
        "sum_distance_bike": group.sum_distance_bike,
        "sum_distance_ebike": group.sum_distance_ebike,
    }


def _get_example_group():
    return _get_group_dict(
        42,
        1,
        "GroupName",
        "Description",

        12.0,
        5,
        2,

        1200,

        12.2,
        12.3,
        12.4,
        12.5
    )


# +++++++++++++++++++++++++++++++++++++++++++


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_detail(request, group_id, *args, **kwargs):
    form_error = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_run ====================================

    exists = Group.objects.filter(id=group_id).exists()
    if not exists:
        form_error.update({
            'code': '404',
            'detail': 'This group does not exist!'
        })
        return JsonResponse(form_error, status=404)

    group = Group.objects.get(id=group_id)

    # ACCESS CONTROL ##############
    # ================================================

    object = _get_group_dict_from_obj(group)

    return JsonResponse(data=object, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_create(request, *args, **kwargs):
    read_name = request.POST.get("name")
    read_description = request.POST.get("description")

    name = None
    description = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_name =====================================

    if not read_name or len(read_name) <= 0:
        response_object.update({
            'code': '400-1',
            'detail': 'Titel darf nicht leer sein!'
        })
        return JsonResponse(response_object, status=400)

    name = read_name

    # ================================================
    # clean_description ==============================

    if read_description and len(str(read_description)) > 0:
        description = str(read_description)

    # ================================================

    instance = Group.objects.create(
        creator=request.user.profile,
        name=name,
        description=description,
    )

    response_object = {
        'code': '201',
        'status': 'successful',
        'id': instance.id,
    }

    return JsonResponse(response_object, status=201)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_edit(request, group_id, *args, **kwargs):
    read_name = request.POST.get("name")
    read_description = request.POST.get("description")

    name = None
    description = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_group ====================================

    exists = Group.objects.filter(id=group_id).exists()
    if not exists:
        response_object.update({
            'code': '404',
            'detail': 'This group does not exist!'
        })
        return JsonResponse(response_object, status=404)

    group = Group.objects.get(id=group_id)

    # ACCESS CONTROL ##############
    if group.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================
    # clean_name =====================================

    if not read_name or len(read_name) <= 0:
        response_object.update({
            'code': '400',
            'detail': "Name mustn't be empty!"
        })
        return JsonResponse(response_object, status=400)

    name = read_name

    # ================================================
    # clean_description ==============================

    if read_description and len(str(read_description)) > 0:
        description = str(read_description)

    # ================================================

    group.creator = request.user.profile

    group.name = name
    group.description = description

    group.save()

    response_object = {
        'code': '200',
        'status': 'successful',
        'id': group.id,
    }
    return JsonResponse(response_object, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_delete(request, group_id, *args, **kwargs):

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_group ====================================

    exists = Group.objects.filter(id=group_id).exists()
    if not exists:
        response_object.update({
            'code': '404',
            'detail': 'This group does not exist!'
        })
        return JsonResponse(response_object, status=404)

    group = Group.objects.get(id=group_id)

    # ACCESS CONTROL ##############
    if group.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================

    group.delete()

    response_object = {
        'code': '200',
        'status': 'successful',
    }
    return JsonResponse(response_object, status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_list_user(request, *args, **kwargs):
    groups = Group.objects.filter(creator=request.user.profile)
    object_list = []

    for group in groups:
        object_list.append(_get_group_dict_from_obj(group))

    return HttpResponse(json.dumps(object_list), content_type="application/json")


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def group_list(request, *args, **kwargs):
    groups = Group.objects.all()
    object_list = []

    for group in groups:
        object_list.append(_get_group_dict_from_obj(group))

    return HttpResponse(json.dumps(object_list),
                        content_type="application/json")
