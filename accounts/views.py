from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from .models import User
from .forms import UserRegisterForm
from .forms import PasswordResetForm
from django.views import View
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "auth/register.html"
    success_url = reverse_lazy("accounts:login")
    form_class = UserRegisterForm
    success_message = "Your account has been created successfully"


class PasswordResetView(View):
    template_name = "auth/password_reset.html"
    form_class = PasswordResetForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if "@" in username:
                kwargs = {"email": username}
            else:
                kwargs = {"username": username}

            try:
                user = User.objects.get(**kwargs)
            except User.DoesNotExist:
                messages.error(request, "Invalid Username or Email")
                return redirect("accounts:password_reset")
            print(
                "Password Reset Link: http://127.0.0.1:8000/accounts/password-reset-confirm/{}/{}".format(
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    default_token_generator.make_token(user),
                )
            )
            return redirect("accounts:password_reset_done")

        return render(request, self.template_name, {"form": form})
