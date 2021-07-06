from django.urls import path
from . import views

app_name = "dialogs"
urlpatterns = [
    path("threads/", views.ThreadListCreate.as_view(), name="threads_list"),
    path(
        "threads/<int:pk>/",
        views.ThreadRetrieveDestroy.as_view(),
        name="threads_detail",
    ),
    path(
        "threads/<int:thread_pk>/messages/", views.messages_list, name="messages_list"
    ),
    path(
        "threads/<int:thread_pk>/messages/<int:message_pk>/",
        views.message,
        name="message",
    ),
    path(
        "threads/<int:thread_pk>/messages/read_until/",
        views.message_read_until,
        name="message_read_until",
    ),
]
