from django.shortcuts import render, redirect
from .models import Question
from .forms import QuestionForm
from taggit.models import Tag
from django.contrib import messages
from django.template.defaultfilters import slugify

def home(request):
    questions = Question.objects.order_by("-create_date")
    return render(request, "home.html", {"questions":questions})

def new_question(request):
    if request.method == "GET":
        return render(request, "new_question.html")
    else:
        new_quest = QuestionForm(request.POST, request.FILES)
        if new_quest.is_valid():
            new_quest_saved = new_quest.save(commit=False)
            new_quest_saved.user = request.user
            new_quest_saved.slug = slugify(new_quest_saved.title)
            new_quest_saved.save()
            new_quest.save_m2m()
            return redirect("forumapp:home")
        else:
            messages.error(request, "Something went wrong, data hasn't been saved. Try again!")
            return render(request, "new_question.html")



