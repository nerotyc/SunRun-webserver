from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .run_views import test_token, user_id, run_detail, run_create, run_edit, run_delete, run_list_user
from .route_views import route_detail, route_create, route_edit, route_delete, route_list_user, route_list
from .group_views import group_detail, group_create, group_edit, group_delete, group_list_user, group_list

# TODO null values (not string)
urlpatterns = [

    path('auth/login/', obtain_auth_token, name='user-login'),
    path('auth/test-token/', test_token, name='test-token'),

    path('user/user-id/', user_id, name='user-id'),

    path('run/<int:run_id>/', run_detail, name='run-detail'),
    path('run/create/', run_create, name='run-create'),
    path('run/edit/<int:run_id>/', run_edit, name='run-edit'),
    path('run/delete/<int:run_id>/', run_delete, name='run-delete'),
    path('run/user/', run_list_user, name='run-list-user'),
    # TODO group list for foreignkeyselector
    # TODO route list for foreignkeyselector

    path('route/<int:route_id>/', route_detail, name='route-detail'),
    path('route/create/', route_create, name='route-create'),
    path('route/edit/<int:route_id>/', route_edit, name='route-edit'),
    path('route/delete/<int:route_id>/', route_delete, name='route-delete'),
    path('route/list/', route_list, name='route-list'),
    path('route/user/', route_list_user, name='route-list-user'),

    path('group/<int:group_id>/', group_detail, name='group-detail'),
    path('group/create/', group_create, name='group-create'),
    path('group/edit/<int:group_id>/', group_edit, name='group-edit'),
    path('group/delete/<int:group_id>/', group_delete, name='group-delete'),
    path('group/list/', group_list, name='group-list'),
    path('group/user/', group_list_user, name='group-list-user'),

]
