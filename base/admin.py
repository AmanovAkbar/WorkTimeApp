from django.contrib import admin
from .models import User, WorkTime, Organization, OrganizationWorkTime
# Register your models here.

admin.site.register(User)

admin.site.register(WorkTime)

admin.site.register(Organization)

admin.site.register(OrganizationWorkTime)