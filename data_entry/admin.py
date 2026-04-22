from django.contrib import admin
from .models import Activity, ActivityPhoto, Project, UserProfile, Work


admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Work)
admin.site.register(Activity)
admin.site.register(ActivityPhoto)
