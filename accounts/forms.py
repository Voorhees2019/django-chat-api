from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        required=True, label="Password", widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        required=True, label="Password Confirmation", widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]


class PasswordResetForm(forms.Form):
    username = forms.CharField(required=True, label="Email or Username")
