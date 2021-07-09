from accounts.models import User
from rest_framework.exceptions import ValidationError
from .models import Message


def read_all_interlocutor_messages(user: User, thread_pk: int) -> None:
    Message.objects.unread().filter(thread__pk=thread_pk).exclude(sender=user).update(
        is_read=True
    )


def read_interlocutor_messages_until(
    user: User, thread_pk: int, message_pk: int
) -> None:
    if message_pk < 1:
        raise ValidationError("[ERROR] Invalid message_pk")

    Message.objects.unread().filter(thread__pk=thread_pk, pk__lte=message_pk).exclude(
        sender=user
    ).update(is_read=True)
