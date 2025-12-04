from django.contrib import admin

from myadmin.models import Role, Permission

# Register your models here.
admin.site.register(Role)
admin.site.register(Permission)