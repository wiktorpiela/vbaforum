from .models import Question, Answer
from django import forms

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ("create_date","user","likes",)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ("question", "likes", "user", "create_date",)