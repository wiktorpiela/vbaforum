from django.contrib import admin
from .models import Question, Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ("create_date","likes",)
    list_display = ("title", "user", "create_date","get_tags",)

    def get_tags(self, obj):
        return ", ".join(tag for tag in obj.tags.names())
    
@admin.register(Answer)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ("question","user","likes","create_date",)
    list_display = ("question","user","create_date",)


