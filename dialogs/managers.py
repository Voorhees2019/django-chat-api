from django.db import models


class MessageManager(models.Manager):
    def read(self):
        return super().get_queryset().filter(is_read=True)

    def unread(self):
        return super().get_queryset().filter(is_read=False)
