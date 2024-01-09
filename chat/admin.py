from django.contrib import admin

from chat.models import UserSetting, Message, Chat

# Register your models here.
admin.site.register(UserSetting)
admin.site.register(Message)
admin.site.register(Chat)
