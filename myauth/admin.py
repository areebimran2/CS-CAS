from django.contrib import admin

from myauth.models import User, UserPreference

admin.site.register(User)
admin.site.register(UserPreference)
