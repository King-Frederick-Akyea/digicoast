from django.contrib import admin

# Register your models here.

from .models import Drone, Medication
admin.site.register(Drone)
admin.site.register(Medication)

