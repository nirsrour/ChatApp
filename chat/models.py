from django.db import models
import uuid


class UserSetting(models.Model):
    full_name = models.TextField(max_length=50)
    email = models.EmailField(unique=True)
    username = models.TextField(max_length=25, unique=True)
    password = models.CharField(max_length=30)

    def __str__(self):
        return self.username


class Chat(models.Model):
    first_user = models.ForeignKey(
        UserSetting, on_delete=models.CASCADE, related_name='first_side')
    second_user = models.ForeignKey(
        UserSetting, on_delete=models.CASCADE, related_name='second_side')
    is_active = models.BooleanField(default=True, name="is_chat_active")

    def __str__(self) -> str:
        status = "active" if self.is_chat_active else "not active"
        return f"the chat between {self.first_user.username} and {self.second_user.username} is {status}"


class Message(models.Model):

    msg = models.TextField(max_length=500)
    sender = models.ForeignKey(
        UserSetting, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ForeignKey(
        UserSetting, on_delete=models.CASCADE, related_name='message_receiver')
    msg_time = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"sender:{self.sender}, receiver:{self.receiver} msg: {self.msg}"

    class Meta:
        ordering = ['-msg_time']
