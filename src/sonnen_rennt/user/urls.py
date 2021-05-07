from django.urls import path, include

from .views import profile_page
from django.contrib.auth.views import (
    PasswordChangeView
#     PasswordResetView,
#     PasswordResetDoneView,
#     PasswordResetConfirmView,
#     PasswordResetCompleteView
)

from django.contrib.auth import views as auth_views

from .views import (register_view, login_view, logout_view,
                    password_change_done,
                    edit_profile,
                    # password_change_view,
                    # password_reset_request,
                    # password_reset_view,
                    # password_reset_confirm_view,
                    # password_reset_complete_view,
                    # password_reset_done_view
                    )

urlpatterns = [
    path('profile/', profile_page, name='profile'),

    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('password_change/', PasswordChangeView.as_view(template_name="user/change_password.html"), name='password_change'),
    path('password_change_done/', password_change_done, name='password_change_done'),
    # path('password_change/', password_change_view, name='password_change'),
    # path('accounts/password_change/done/', password_change_view, name='password_change_done'),
    # path('password_reset/', password_reset_request,  # PasswordResetView.as_view(template_name='user/password_reset.html')
    #      name='password_reset'),
    # path('password_reset_confirm/', PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
    #      name='password_reset_confirm'),
    # path('password_reset_complete/', PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
    #      name='password_reset_complete'),
    # path('password_reset_done/', PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
    #      name='password_reset_done'),
    # path('accounts/password_reset/done/', password_reset_view, name='password_reset_done')

    path('edit_profile/', edit_profile, name='edit_profile'),

]
#  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']

# TODO rewrite /login/ to /user/login/
