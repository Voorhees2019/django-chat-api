from accounts.models import User
from rest_framework.exceptions import ValidationError
from .models import Thread, Message


def user_has_thread_permission(user: User, thread_pk: int) -> None:
    """
    Function that checks if user has permission to access the thread.
    """
    thread = Thread.objects.filter(pk=thread_pk, participants=user).exists()
    if not thread:
        raise ValidationError(
            "[ERROR] You don't have permissions to access this thread"
        )


def user_has_message_permission(user: User, message_pk: int) -> None:
    """
    Function that checks if user has permission to access the message.
    """
    sender = getattr(Message.objects.filter(pk=message_pk).first(), "sender", False)
    if not sender:
        raise ValidationError("[ERROR] Message does not exist")

    if not user == sender:
        raise ValidationError(
            "[ERROR] You don't have permissions to access this message"
        )


def read_all_interlocutor_messages(user: User, thread_pk: int) -> None:
    Message.objects.unread().filter(thread__pk=thread_pk).exclude(sender=user).update(
        is_read=True
    )


def read_interlocutor_messages_before(
    user: User, thread_pk: int, message_pk: int
) -> None:
    if message_pk < 1:
        raise ValidationError("[ERROR] Invalid message_pk")

    Message.objects.unread().filter(thread__pk=thread_pk, pk__lte=message_pk).exclude(
        sender=user
    ).update(is_read=True)
