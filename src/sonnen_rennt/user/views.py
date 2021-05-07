from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from .forms import UserRegisterForm, ProfileUpdateForm


def register_forward(request):
    return redirect("/user/register/")


def login_forward(request):
    return redirect("/user/login/")


def logout_forward(request):
    return redirect("/user/logout/")


def register_view(request, *args, **kargs):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            print("preSave")
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account wurde erstellt! Anmeldung jetzt möglich.')
            return redirect('login')

    else:
        form = UserRegisterForm()

    messages.warning(request, "Mit der Registrierung bestätigen Sie, dass Sie damit einverstanden sind, dass alle Daten außer Email-Adressen, Passwörter und Laufdaten, die keiner Grupe zugeordnet werden, öffentlich einsehbar sind. Mehr dazu auf unserer Datenschutzseite.")

    return render(request, 'user/register.html', {'form': form})


def login_view(request, *args, **kargs):
    if request.user.is_authenticated:
        return redirect('/')
    # else:
    #     return auth_views.LoginView.as_view(template_name='users/login.html')

    form = AuthenticationForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Anmelden erfolgreich!')

            next = request.GET.get('next', '')
            if len(next) > 0:
                print("next:", next)
                return redirect(next)
            else:
                print("nonext:")
                return redirect("/")

        else:
            form = AuthenticationForm()
            messages.error(request, f'Anmelden fehlgeschlagen!')
            # Return an 'invalid login' error message.

    context = {
        'form': form
    }

    return render(request, 'user/login.html', context)


def password_change_done(request):
    messages.success(request, "Passwort erfolgreich geändert!")
    return redirect("/user/profile/")


def logout_view(request, *args, **kargs):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == "POST":
        logout(request)
        messages.success(request, f'Abmelden erfolgreich!')
        return redirect('/login/')

    return render(request, 'user/logout.html', {})


# TODO IN PRODUCTION: images from static files instead of media root
@login_required
def profile_page(request):
    return render(request, 'user/profile.html', {})


@login_required
def password_change_view(request):
    return PasswordChangeForm(request.user)
    # return render(request, 'user/password_change.html', {})


# def password_reset_request(request):
#     if request.method == "POST":
#         password_reset_form = PasswordResetForm(request.POST)
#         if password_reset_form.is_valid():
#             data = password_reset_form.cleaned_data['email']
#             associated_users = User.objects.filter(Q(email=data))
#             if associated_users.exists():
#                 for user in associated_users:
#                     subject = "Password Reset Requested"
#                     email_template_name = "user/password_reset_email.txt"
#                     c = {  # TODO
#                         "email": user.email,
#                         'domain': '127.0.0.1:8000',
#                         'site_name': 'Website',
#                         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                         "user": user,
#                         'token': default_token_generator.make_token(user),
#                         'protocol': 'http',
#                     }
#                     email = render_to_string(email_template_name, c)
#                     try:
#                         send_mail(subject, email, 'admin@robinh.xyz', [user.email], fail_silently=False)
#                     except BadHeaderError:
#                         return HttpResponse('Invalid header found.')
#                     return redirect("/user/password_reset_done/")
#     password_reset_form = PasswordResetForm()
#     return render(request=request, template_name="user/password_reset.html",
#                   context={"password_reset_form": password_reset_form})
#
# # def password_reset_view(request):
# #     form = PasswordResetForm()
# #
# #     if request.method == "POST":
# #         form = PasswordResetForm(request.POST)
# #
# #         if form.is_valid():
# #             form.save()
# #
# #     context = {
# #         'form': form
# #     }
# #
# #     return render(request, 'user/password_reset.html', context)
# #
# #
# # def password_reset_confirm_view(request):
# #     form = PasswordResetForm()
# #
# #     context = {
# #         'form': form
# #     }
# #
# #     return render(request, 'user/password_reset_confirm.html', context)
# #
# #
# # def password_reset_complete_view(request):
# #     form = PasswordResetForm()
# #
# #     context = {
# #         'form': form
# #     }
# #
# #     return render(request, 'user/password_reset.html', context)
# #
# #
# # def password_reset_done_view(request):
# #     form = PasswordResetForm()
# #
# #     context = {
# #         'form': form
# #     }
# #
# #     return render(request, 'user/password_reset.html', context)
#
#
# # examples
# # class ExampleViewOne(View):
# #     def get(self, request, *args, **kwargs):
# #         return render(request, "root.html", {})
# #
# #     # def post(self, request, *args, **kwargs):
# #     #     return render(request, "root.html", {})
# #
# #
# # def example_function_based_view(request, *args, **kwargs):
# #     print(request.method)
# #     return render(request, "root.html", {})

@login_required
def edit_profile(request):
    initial = {
        'username': request.user.username,
        'name': request.user.profile.name,
        'email': request.user.email,
    }
    form = ProfileUpdateForm(initial=initial)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST)

        updated_something = False

        if form.is_valid():
            old_profile = request.user.profile

            if old_profile.name != form.cleaned_data.get('name'):
                old_profile.name = form.cleaned_data.get('name')
                old_profile.save()
                updated_something = True
                messages.success(request, "Name erfolgreich aktualisiert!")

            new_username = form.cleaned_data.get('username')

            username_updated = (request.user.username != new_username)
            email_updated = (request.user.email != form.cleaned_data.get('email'))

            if username_updated or email_updated:
                if username_updated:
                    username_taken = User.objects.filter(username=new_username).exists()

                    if username_taken:
                        messages.error(request, "Der gewählte Nutzername ist bereits vergeben!")
                    if len(new_username) <= 0:
                        messages.error(request, "der Nutzername darf nicht leer sein!")
                    else:
                        request.user.username = new_username  # TODO check sonderzeichen
                        updated_something = True
                        messages.success(request, "Nutzername erfolgreich geändert!")

                if email_updated:
                    request.user.email = form.cleaned_data.get('email')
                    updated_something = True
                    request.user.save()
                    messages.success(request, "Email erfolgreich aktualisiert!")

                request.user.save()

            if updated_something:
                return redirect('/user/profile/')
            else:
                return redirect('/user/edit_profile/')

    context = {
        'form': form
    }
    return render(request, "user/edit_profile.html", context)
