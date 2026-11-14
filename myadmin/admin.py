from django.contrib import admin

from myadmin.models import Permission, Role

admin.site.register(Role)
admin.site.register(Permission)
