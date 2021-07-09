from django.urls import path
from . import views

app_name = "dialogs"
urlpatterns = [
    path("threads/", views.ThreadListCreate.as_view(), name="thread_list"),
    path(
        "threads/<int:pk>/",
        views.ThreadRetrieveDestroy.as_view(),
        name="thread_detail",
    ),
    path(
        "threads/<int:thread_pk>/messages/",
        views.MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="message_list",
    ),
    path(
        "messages/<int:pk>/",
        views.MessageViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="message_detail",
    ),
    path(
        "threads/<int:thread_pk>/messages/read_until/",
        views.MessagesReadUntil.as_view(),
        name="messages_read_until",
    ),
]
