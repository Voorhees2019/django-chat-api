from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.models import User
from .models import Thread, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ThreadSerializer(serializers.ModelSerializer):
    num_unread_messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = (
            "id",
            "participants",
            "num_unread_messages",
            "last_message",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get("request", None)

    def get_last_message(self, obj):
        try:
            return Message.objects.filter(thread=obj.pk).last().text
        except AttributeError:
            return "No messages yet"

    def get_num_unread_messages(self, obj):
        return Message.objects.filter(thread=obj.pk, is_read=False).count()

    def create(self, validated_data):
        thread = (
            Thread.objects.filter(participants=validated_data.get("participants")[0])
            .filter(participants=validated_data.get("participants")[1])
            .first()
        )
        # Create a new thread if it doesn't exist between passed users
        if not thread:
            thread = super().create(validated_data=validated_data)
        return thread

    def validate(self, data):
        """
        Function that checks participants to create a new thread. There must be two
        participants in thread and the the user who is sending request must be one of them.
        """
        participants = data.get("participants", None)

        if not participants:
            raise ValidationError("[ERROR] You must provide participants")

        if len(set(participants)) == 1 or len(participants) > 2:
            raise ValidationError(
                "[ERROR] Thread must contain 2 different participants"
            )

        if not self.request or not self.request.user.is_authenticated:
            raise ValidationError("[ERROR] User is not authenticated")

        if self.request.user not in participants:
            raise ValidationError("[ERROR] You can not create a thread without you in")
        return data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            "text",
            "sender",
            "thread",
            "is_read",
        )
