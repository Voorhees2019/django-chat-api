from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import (
    ThreadSerializer,
    MessageSerializer,
)
from .models import Thread, Message
from .services import (
    read_interlocutor_messages_until,
    read_all_interlocutor_messages,
)
from .permissions import IsThreadParticipant, MessagePermission


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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ThreadRetrieveDestroy(generics.RetrieveDestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated, IsThreadParticipant]

    def get_queryset(self):
        return Thread.objects.all()

    def delete(self, request, *args, **kwargs):
        thread = self.get_object()  # checking thread permissions here

        # delete thread if there are no participants
        if thread.participants.count() <= 1:
            return self.destroy(request, *args, **kwargs)

        # delete participant from thread
        thread.participants.remove(self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsThreadParticipant]

    def get_queryset(self):
        return Message.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Lists a queryset.
        """
        thread = get_object_or_404(Thread, pk=self.kwargs.get("thread_pk"))
        # checking thread permissions
        self.check_object_permissions(request=self.request, obj=thread)

        queryset = self.get_queryset().filter(thread=thread)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Creates a Message instance.
        """
        thread = get_object_or_404(Thread, pk=self.kwargs.get("thread_pk"))
        # checking thread permissions
        self.check_object_permissions(request=self.request, obj=thread)

        # read all previous interlocutor's messages before sending a new one
        read_all_interlocutor_messages(user=request.user, thread_pk=thread.pk)

        # defining request.user as a sender of created message and specifying a thread the message belongs to
        request.data.update(sender=request.user.id, thread=self.kwargs.get("thread_pk"))
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        msg = serializer.save()
        return Response(self.get_serializer(msg).data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["list", "create"]:
            self.permission_classes = [permissions.IsAuthenticated, IsThreadParticipant]
        else:
            self.permission_classes = [permissions.IsAuthenticated, MessagePermission]
        return super().get_permissions()


class MessagesReadUntil(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsThreadParticipant]

    def post(self, request, *args, **kwargs):
        thread = get_object_or_404(Thread, pk=self.kwargs.get("thread_pk"))
        # checking thread permissions
        self.check_object_permissions(request=self.request, obj=thread)

        message_pk = request.data.get("message_id")

        read_interlocutor_messages_until(
            user=request.user, thread_pk=thread.pk, message_pk=message_pk
        )

        return Response({"action": "Done"}, status=status.HTTP_200_OK)
