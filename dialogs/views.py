from django.core.paginator import Paginator
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    ThreadSerializer,
    MessageSerializer,
)
from .models import Thread, Message
from .services import (
    user_has_thread_permission,
    user_has_message_permission,
    read_interlocutor_messages_before,
    read_all_interlocutor_messages,
)
from .permissions import IsParticipant


class ThreadListCreate(generics.ListCreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # GET list of Threads that belongs only to user who is making request
        return Thread.objects.filter(participants=self.request.user).order_by(
            "-created_at"
        )

    def post(self, request, *args, **kwargs):

        serializer = ThreadSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(serializer.data)


class ThreadRetrieveDestroy(generics.RetrieveDestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Thread.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            thread = Thread.objects.get(pk=self.kwargs.get("pk"))
        except Thread.DoesNotExist:
            raise ValidationError("[ERROR] Thread doesn't exist")

        self.check_object_permissions(request=self.request, obj=thread)

        # delete thread if there are no participants
        if thread.participants.count() <= 1:
            return self.destroy(request, *args, **kwargs)

        # delete participant from thread
        thread.participants.remove(self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def messages_list(request, thread_pk: int):

    user_has_thread_permission(user=request.user, thread_pk=thread_pk)

    if request.method == "GET":
        messages = Message.objects.filter(thread__pk=thread_pk).order_by("-created_at")
        paginator = Paginator(messages, settings.REST_FRAMEWORK.get("PAGE_SIZE"))
        page = paginator.get_page(request.GET.get("page"))
        serializer = MessageSerializer(page, many=True)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        # read all previous interlocutor's messages before sending a new one
        read_all_interlocutor_messages(user=request.user, thread_pk=thread_pk)

        request.data.update(sender=request.user.id, thread=thread_pk)

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        message = serializer.save()
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def message(request, thread_pk: int, message_pk: int):

    user_has_thread_permission(user=request.user, thread_pk=thread_pk)
    user_has_message_permission(user=request.user, message_pk=message_pk)

    # Must not wrap in try block because the function above have already checked if that message exists
    message = Message.objects.get(pk=message_pk)

    if request.method == "GET":
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = MessageSerializer(
            data=request.data, instance=message, partial=True
        )
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        message = serializer.save()
        return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def message_read_until(request, thread_pk: int):
    user_has_thread_permission(user=request.user, thread_pk=thread_pk)

    message_pk = request.data.get("message_id")

    read_interlocutor_messages_before(
        user=request.user, thread_pk=thread_pk, message_pk=message_pk
    )

    return Response({"action": "Done"}, status=status.HTTP_200_OK)
