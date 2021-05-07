from PIL import Image
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# class UserPasswordReset(PasswordResetForm):


# class UserPasswordChangeForm(PasswordChangeForm):
    # email = forms.EmailField()
    #
    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password1', 'password2']

# class UserUpdateForm(forms.ModelForm):
#     email = forms.EmailField()
#
#     class Meta:
#         model = User
#         fields = ['username', 'email']


class ProfileUpdateForm(forms.Form):

    username = forms.CharField(
        max_length=250,
    )

    name = forms.CharField(max_length=200)

    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['username', 'name', 'email']
