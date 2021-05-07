from tokenize import group

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from sonnen_rennt import settings
from user.views import register_forward, login_forward, logout_forward
from sonnen_rennt.views import root_view, contact_view, imprint_view
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),

    path('login/', login_forward, name='login'),
    # path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('register/', register_forward, name='register'),
    path('logout/', logout_forward, name='logout'),

    path('dashboard/', include('dashboard.urls'), name='dashboard'),
    path('user/', include('user.urls'), name='user'),
    path('run/', include('run.urls'), name='run'),
    path('strava-run/', include('strava_run.urls'), name='strava-run'),
    path('route/', include('route.urls'), name='route'),
    path('group/', include('group.urls'), name='group'),

    path('contact/', contact_view, name='contact'),
    path('imprint/', imprint_view, name='imprint'),

    path('api/', include('api.urls'), name='api'),

    # path('reset_password/',
    #      auth_views.PasswordResetView.as_view(template_name="user/password_reset.html"),
    #      name="reset_password"),
    #
    # path('reset_password_sent/',
    #      auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_sent.html"),
    #      name="password_reset_done"),
    #
    # path('reset/<uidb64>/<token>/',
    #      auth_views.PasswordResetConfirmView.as_view(template_name="user/password_reset_form.html"),
    #      name="password_reset_confirm"),
    #
    # path('reset_password_complete/',
    #      auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_done.html"),
    #      name="password_reset_complete"),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
