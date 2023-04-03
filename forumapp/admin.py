from django.contrib import admin
from .models import Question, Answer

class CreateDate(admin.ModelAdmin):
    readonly_fields = ("create_date","likes","user",)

class ReadOnlyAnswer(admin.ModelAdmin):
    readonly_fields = ("question","user","likes","create_date",)

admin.site.register(Question, CreateDate)
admin.site.register(Answer, ReadOnlyAnswer)
