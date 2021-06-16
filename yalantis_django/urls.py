import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    path("", views.home, name="home"),
    path("about-us/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("authors/", views.authors, name="authors"),
    path("accounts/", include("accounts.urls")),
]
