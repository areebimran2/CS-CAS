from django.contrib import admin

from myadmin.models import Role, Permission

admin.site.register(Role)
admin.site.register(Permission)