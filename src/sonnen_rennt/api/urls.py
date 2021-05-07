from django.urls import path, include

from api.views import test_api

urlpatterns = [
    path('v1/', include("api.v1.urls"), name='v1'),
]

