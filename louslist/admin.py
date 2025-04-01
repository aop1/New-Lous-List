from django.contrib import admin

from .models import User, Prefix, Schedule, Course, Comment, SearchTerm


admin.site.register(User)
admin.site.register(Prefix)
admin.site.register(Schedule)
admin.site.register(Course)
admin.site.register(Comment)
admin.site.register(SearchTerm)
