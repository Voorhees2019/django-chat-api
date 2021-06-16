from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


def login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("home")
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("login")
    return render(request, "auth/login.html", {})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "That username is already taken")
                return redirect("register")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "That email is being used")
                    return redirect("register")
                else:
                    # Looks good
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    messages.success(
                        request, "Your account has been created successfully"
                    )
                    # login after registration
                    auth.login(request, user)
                    return redirect("home")
        else:
            messages.error(request, "Passwords did not match")
            return redirect("register")
    return render(request, "auth/register.html", {})


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, "You are now logged out")
    return redirect("home")


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            username = password_reset_form.cleaned_data["username"]
            if "@" in username:
                kwargs = {"email": username}
            else:
                kwargs = {"username": username}

            try:
                user = User.objects.get(**kwargs)
            except User.DoesNotExist:
                messages.error(request, "Invalid Username or Email")
                return redirect("password_reset")
            print(
                "Password Reset Link: http://127.0.0.1:8000/accounts/password-reset-confirm/{}/{}".format(
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    default_token_generator.make_token(user),
                )
            )

            return redirect("password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request, "auth/password_reset.html", {"form": password_reset_form})
