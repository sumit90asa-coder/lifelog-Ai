from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Tag)
admin.site.register(Metric)
admin.site.register(Streak)
admin.site.register(Entry)
