
from django.urls import path

from dashboard.views import default_view, community_view, user_view

app_name = 'dashboard'
urlpatterns = [
    path('', default_view),
    path('community/', community_view, name='community'),
    path('my/', user_view, name='my'),
    # path('', dashboard_forward),
]
