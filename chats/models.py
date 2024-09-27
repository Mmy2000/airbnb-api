import uuid

from django.db import models

from useraccount.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        User,
        related_name="conversations",
        null=True,
        blank=True    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversations"
        verbose_name_plural = "Conversations"

    def remove_user(self, user):
        self.users.remove(user)

    def __str__(self):
        return str(self.users)


class ConversationMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    body = models.TextField()
    sent_to = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.SET_NULL
        , null=True, blank=True
    )
    created_by = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conversation Message"
        verbose_name_plural = "Conversation Message"

    def __str__(self):
        return str(self.conversation)


@receiver(pre_delete, sender=User)
def remove_user_from_conversations(sender, instance, **kwargs):
    # Remove user from all conversations
    instance.conversations.clear()
