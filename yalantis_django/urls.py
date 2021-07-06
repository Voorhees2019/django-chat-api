import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from .settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("about-us/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("authors/", views.authors, name="authors"),
    path("accounts/", include("accounts.urls")),
    path("api/v1/dialogs/", include("dialogs.urls")),
    path("api/v1/get-auth-token/", obtain_jwt_token),
]

if DEBUG:
    urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
