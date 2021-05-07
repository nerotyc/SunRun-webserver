from django.http import HttpResponse


def test_api(request, *args, **kargs):
    return HttpResponse("asdfasdf")
