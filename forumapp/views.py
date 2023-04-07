from django.shortcuts import render, redirect, get_object_or_404
from .models import Question
from .forms import QuestionForm
from taggit.models import Tag
from django.contrib import messages
from django.template.defaultfilters import slugify
from accounts.models import UserProfile

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
        
def question_details(request, questID):
    quest = get_object_or_404(Question, pk=questID)
    author_name = quest.user
    author_avatar = quest.user.userprofile.avatar
    author_role = quest.user.userprofile.role
    author_joined = quest.user.date_joined
    roles = UserProfile.roles
    for short, long in roles:
        if short == author_role:
            break   
    return render(request, "question_details.html", {"question":quest,
                                                     "author_name":author_name,
                                                     "author_avatar":author_avatar,
                                                     "author_joined":author_joined,
                                                     "author_role":long})

def display_collection(request, type):
    typeToReturn="questions" if type=="quest" else "answers"
    return render(request, "display_collection.html", {"type":typeToReturn,
                                                       "questions":"questions",
                                                       "answers":"answers"})



