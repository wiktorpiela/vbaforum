from django.contrib import admin
from .models import Question, Answer, SendEmailMessage

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ("create_date","likes","user",)
    list_display = ("title", "user", "create_date","get_tags",)

    def get_tags(self, obj):
        return ", ".join(tag for tag in obj.tags.names())
    
@admin.register(Answer)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ("question","user","likes","create_date",)
    list_display = ("question","user","create_date",)





