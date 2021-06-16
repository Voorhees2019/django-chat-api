from django import forms


class PasswordResetForm(forms.Form):
    username = forms.CharField(required=True, label="Email or Username")
