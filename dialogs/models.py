from django.db import models
from accounts.models import User
from .managers import MessageManager


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread #{self.id}"


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="thread_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    objects = MessageManager()

    def __str__(self):
        return f"Message from {self.sender} to {self.thread}"
