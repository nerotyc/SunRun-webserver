
from django.urls import path
from django.contrib.auth.decorators import login_required

from route.views import (dashboard_forward,
                         dashboard_view,
                         help,
                         RouteDetailView,
                         RouteCreateView,
                         RouteDeleteView,
                         RouteUpdateView,
                         RouteListView,
                         # list_group_view,
                         RouteListUserView
                     )

app_name = 'route'
urlpatterns = [
    path('', dashboard_forward),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('help/', help, name='help'),

    path('detail/<int:route_id>/', login_required(RouteDetailView.as_view()), name='detail'),
    path('create/', login_required(RouteCreateView.as_view()), name='create'),
    path('delete/<int:route_id>/', login_required(RouteDeleteView.as_view()), name='create'),
    path('edit/<int:route_id>/', login_required(RouteUpdateView.as_view()), name='edit'),
    path('list/', login_required(RouteListView.as_view()), name='list'),
    # path('list-group/', list_group_view, name='list_group'),
    path('list-user/', login_required(RouteListUserView.as_view()), name='list_user'),  # TODO
]
