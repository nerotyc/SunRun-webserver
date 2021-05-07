
from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test

from run.views import (dashboard_forward, dashboard_view, RunDetailView,
                       RunCreateView, RunDeleteView, RunUpdateView,
                       # RunListView,
                       # list_group_view,
                       RunListUserView
                       )

app_name = 'run'
urlpatterns = [
    path('', dashboard_forward),
    path('dashboard/', dashboard_view, name='dashboard'),

    path('detail/<int:run_id>/', login_required(RunDetailView.as_view()), name='detail'),
    path('create/', login_required(RunCreateView.as_view()), name='create'),
    path('delete/<int:run_id>/', login_required(RunDeleteView.as_view()), name='create'),
    path('edit/<int:run_id>/', login_required(RunUpdateView.as_view()), name='edit'),
    # path('list/', login_required(RunListView.as_view()), name='list'),
    # path('list-group/', list_group_view, name='list_group'),  # TODO
    path('list-user/', login_required(RunListUserView.as_view()), name='list_user'),  # TODO
]
