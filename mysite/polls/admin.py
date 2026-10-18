from django.contrib import admin

from mysite.polls.models import Choice, Question

admin.site.register(Question)
admin.site.register(Choice)
