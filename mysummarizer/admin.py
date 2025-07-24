from django.contrib import admin
from .models import UserHistory

class MyHistory(admin.ModelAdmin):
    list_display=['user','created_at','updated_at']

admin.site.register(UserHistory,MyHistory)

# Register your models here.
