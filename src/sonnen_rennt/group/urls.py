
from django.urls import path
from django.contrib.auth.decorators import login_required

from group import score_updater
from group.views import (
                        dashboard_forward,
                        dashboard_view,
                        help_view,

                        GroupDetailView,
                        GroupCreateView,
                        GroupDeleteView,
                        GroupUpdateView,
                        GroupListView,
                        GroupListUserView,
                        GroupStatsView,
                        StravaGroupStatsView
                     )

app_name = 'group'
urlpatterns = [
    path('', dashboard_forward),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('score-help/', help_view, name='help'),

    path('detail/<int:group_id>/', login_required(GroupDetailView.as_view()), name='detail'),
    path('stats/<int:group_id>/', login_required(GroupStatsView.as_view()), name='stats'),
    path('strava-stats/', login_required(StravaGroupStatsView.as_view()), name='strava-stats'),

    path('create/', login_required(GroupCreateView.as_view()), name='create'),
    path('delete/<int:group_id>/', login_required(GroupDeleteView.as_view()), name='create'),
    path('edit/<int:group_id>/', login_required(GroupUpdateView.as_view()), name='edit'),
    path('list/', login_required(GroupListView.as_view()), name='list'),
    # path('list-group/', list_group_view, name='list_group'),  # TODO
    path('list-user/', login_required(GroupListUserView.as_view()), name='list_user'),  # TODO


    # path('update', login_required(score_updater.update_view), name='list_user'),  # TODO
]
