from django.contrib import admin

from myauth.models import User, UserPreference, Permission, Role

admin.site.register(User)
admin.site.register(UserPreference)
admin.site.register(Permission)
admin.site.register(Role)
