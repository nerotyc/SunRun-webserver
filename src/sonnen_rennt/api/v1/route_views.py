
from django.http import JsonResponse

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from route.models import Route


def _get_route_dict(
        route_id, title, distance, description,
        link, creator_id, elevation_gain
    ):

    dic = {
        "id": route_id,
        "creator_id": creator_id,
        "title": title,
        "distance": distance,
        "elevation_gain": elevation_gain,
        "description": description,
        "link": link,
    }

    if description:
        dic.update({"description": description})

    if link:
        dic.update({"link": link})

    return dic


def _get_route_dict_from_obj(route: Route):
    return {
        "id": route.id,
        "title": route.title,
        "distance": route.distance,
        "description": route.description,
        "link": route.link,
        "creator_id": route.creator.id,
        "elevation_gain": route.elevation_gain,
    }


def _get_example_route():
    return _get_route_dict(
        42,
        "RouteTitle",
        12.2,
        "Description",
        "https://google.com",
        1,
        1234
    )


# +++++++++++++++++++++++++++++++++++++++++++


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_detail(request, route_id, *args, **kwargs):
    form_error = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_route ====================================

    exists = Route.objects.filter(id=route_id).exists()
    if not exists:
        form_error.update({
            'code': '404',
            'detail': 'This route does not exist!'
        })
        return JsonResponse(form_error, status=404)

    route = Route.objects.get(id=route_id)

    # ACCESS CONTROL ##############
    # ================================================

    object = _get_route_dict_from_obj(route)

    return JsonResponse(data=object, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_create(request, *args, **kwargs):
    read_title = request.POST.get("title")
    read_distance = request.POST.get("distance")
    read_elevation_gain = request.POST.get("elevation_gain")
    read_description = request.POST.get("description")
    read_link = request.POST.get("link")

    title = None
    distance = None
    elevation_gain = None
    description = None
    link = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_title ====================================

    if not read_title or len(read_title) <= 0:
        response_object.update({
            'code': '400-1',
            'detail': 'Titel darf nicht leer sein!'
        })
        return JsonResponse(response_object, status=400)

    title = read_title

    # ================================================
    # clean_distance =================================

    if read_distance:
        read_distance = float(read_distance)

    if read_distance is None:
        response_object.update({
            'code': '400-2',
            'detail': "Distance mustn't be empty!"
        })
        return JsonResponse(response_object, status=400)

    if read_distance > 5000.0:
        response_object.update({
            'code': '400-3',
            'detail': 'Distances over 5000 km are not allowed!'
        })
        return JsonResponse(response_object, status=400)

    if read_distance <= 0:
        response_object.update({
            'code': '400-4',
            'detail': 'Distances must be longer than 0.0 km!'
        })
        return JsonResponse(response_object, status=400)

    distance = float(read_distance)

    # ================================================
    # clean_elevation_gain ===========================

    read_elevation_gain = float(read_elevation_gain)

    if read_elevation_gain is None:
        elevation_gain = 0.0

    else:
        if read_elevation_gain > 10000.0:
            response_object.update({
                'code': '400-5',
                'detail': 'Height differences over 5000m are not allowed!'
            })
            return JsonResponse(response_object, status=400)
        if read_elevation_gain < 0:
            response_object.update({
                'code': '400-6',
                'detail': "Height differences mustn't be negative!"
            })
            return JsonResponse(response_object, status=400)

        elevation_gain = read_elevation_gain

    # ================================================
    # clean_description ==============================

    if read_description and len(str(read_description)) > 0:
        description = str(read_description)

    # ================================================
    # clean_link =====================================

    if read_link and len(str(read_link)) > 0:
        link = str(read_link)

    # ================================================

    instance = Route.objects.create(
        creator=request.user.profile,

        title=title,
        distance=distance,
        elevation_gain=elevation_gain,
        description=description,
        link=link
    )

    print("successssss")

    response_object = {
        'code': '201',
        'status': 'successful',
        'id': instance.id,
    }

    return JsonResponse(response_object, status=201)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_edit(request, route_id, *args, **kwargs):
    read_title = request.POST.get("title")
    read_distance = request.POST.get("distance")
    read_elevation_gain = request.POST.get("elevation_gain")
    read_description = request.POST.get("description")
    read_link = request.POST.get("link")

    title = None
    distance = None
    elevation_gain = None
    description = None
    link = None

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_route ====================================

    exists = Route.objects.filter(id=route_id).exists()
    if not exists:
        response_object.update({
            'code': '404',
            'detail': 'This route does not exist!'
        })
        return JsonResponse(response_object, status=404)


    route = Route.objects.get(id=route_id)

    # ACCESS CONTROL ##############
    if route.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================

    # ================================================
    # clean_title ====================================

    if not read_title or len(read_title) <= 0:
        response_object.update({
            'code': '400',
            'detail': "Title mustn't be empty!"
        })
        return JsonResponse(response_object, status=400)

    title = read_title

    # ================================================
    # clean_distance =================================

    if read_distance:
        read_distance = float(read_distance)

    if read_distance is None:
        response_object.update({
            'code': '400-3',
            'detail': "Distance mustn't be empty!"
        })
        return JsonResponse(response_object, status=400)

    if read_distance > 5000.0:
        response_object.update({
            'code': '400-4',
            'detail': 'Distances over 5000 km are not allowed!'
        })
        return JsonResponse(response_object, status=400)

    if read_distance <= 0:
        response_object.update({
            'code': '400-5',
            'detail': 'Distances must be longer than 0.0 km!'
        })
        return JsonResponse(response_object, status=400)

    distance = float(read_distance)

    # ================================================
    # clean_elevation_gain ===========================

    read_elevation_gain = float(read_elevation_gain)

    if read_elevation_gain is None:
        elevation_gain = 0.0

    else:
        if read_elevation_gain > 10000.0:
            response_object.update({
                'code': '400-6',
                'detail': 'Height differences over 5000m are not allowed!'
            })
            return JsonResponse(response_object, status=400)
        if read_elevation_gain < 0:
            response_object.update({
                'code': '400-7',
                'detail': "Height differences mustn't be negative!"
            })
            return JsonResponse(response_object, status=400)

        elevation_gain = read_elevation_gain

    # ================================================
    # clean_description ==============================

    if read_description and len(str(read_description)) > 0:
        description = str(read_description)

    # ================================================
    # clean_link =====================================

    if read_link and len(str(read_link)) > 0:
        link = str(read_link)

    # ================================================

    route.creator = request.user.profile

    route.title = title
    route.distance = distance
    route.elevation_gain = elevation_gain

    route.description = description
    route.link = link

    route.save()

    response_object = {
        'code': '200',
        'status': 'successful',
        'id': route.id,
    }
    return JsonResponse(response_object, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_delete(request, route_id, *args, **kwargs):

    response_object = {
        'code': '0',
        'status': 'error',
        'detail': 'unknown error'
    }

    # ================================================
    # clean_route ====================================

    exists = Route.objects.filter(id=route_id).exists()
    if not exists:
        response_object.update({
            'code': '404-1',
            'detail': 'This route does not exist!'
        })
        return JsonResponse(response_object, status=404)


    route = Route.objects.get(id=route_id)

    # ACCESS CONTROL ##############
    if route.creator.user.id != request.user.id:
        response_object.update({
            'code': '401',
            'detail': 'Insufficient rights!'
        })
        return JsonResponse(response_object, status=401)

    # ================================================

    route.delete()

    response_object = {
        'code': '200',
        'status': 'successful',
    }
    return JsonResponse(response_object, status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_list_user(request, *args, **kwargs):
    routes = Route.objects.filter(creator=request.user.profile)
    object_list = []

    for route in routes:
        object_list.append(_get_route_dict_from_obj(route))

    return JsonResponse(object_list, safe=False, status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def route_list(request, *args, **kwargs):
    routes = Route.objects.all()
    object_list = []

    for route in routes:
        object_list.append(_get_route_dict_from_obj(route))

    return JsonResponse(object_list, safe=False, status=200)
