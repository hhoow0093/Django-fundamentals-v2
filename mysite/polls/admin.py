from django.contrib import admin

from mysite.polls.models import Choice, Question


class ChoiceInline(admin.TabularInline):  # type: ignore
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):  # type: ignore
    fieldsets = [
        ("Questions", {"fields": ["question_text"]}),
        ("Date information", {"fields": ["published_date"]}),
    ]

    inlines = [ChoiceInline]

    list_display = ["question_text", "published_date", "was_published_recently"]
    list_filter = ["published_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
