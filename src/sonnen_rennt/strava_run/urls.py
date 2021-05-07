
from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test

from .views import StravaRunDetailView, StravaRunListView, forward


app_name = 'strava-run'
urlpatterns = [
    path('detail/<int:run_id>/', login_required(StravaRunDetailView.as_view()), name='detail'),
    path('list/', login_required(StravaRunListView.as_view()), name='list_user'),

    path('forward/', forward, name='forward')
]
