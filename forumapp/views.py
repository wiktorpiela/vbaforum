from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from taggit.models import Tag
from django.contrib import messages
from django.template.defaultfilters import slugify
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Q

def home(request):
    questions = Question.objects.order_by("-create_date")
    return render(request, "home.html", {"questions":questions})

@login_required
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

    quest.is_your = True if quest.user == request.user else False
    quest.is_liked = True if quest.likes.filter(id=request.user.id).exists() else False

    answers = Answer.objects.filter(question = quest).order_by("-create_date")

    for answer in answers:
        if answer.likes.filter(id=request.user.id).exists():
            answer.is_liked = True
        else:
            answer.is_liked = False

    for answer in answers:
        if answer.user == request.user:
            answer.is_your = True
        else:
            answer.is_your = False

    return render(request, "question_details.html", {"question":quest,
                                                     "answers":answers})

@login_required
def add_answer(request, questID):
    quest = get_object_or_404(Question, pk=questID)
    if request.method == "GET":
        return render(request, "add_answer.html",{"question":quest})
    else:
        form = AnswerForm(request.POST, request.FILES)
        stopNotification = quest.user.userprofile.stop_notifications

        if form.is_valid() and not stopNotification:
            new_answer = form.save(commit=False)
            new_answer.question = quest
            new_answer.user = request.user
            new_answer.save()

            author_mail = request.user.username
            email = EmailMessage(
                f"Your question '{quest.title}' has been asnwered by {request.user.username}",
                f"""Hi, <br>
                {request.user.username} has just added the answer to your question!
                Content of the response:
                {new_answer.text} <br>
                Best regards, VBA forum Team""",
                settings.DEFAULT_FROM_EMAIL,
                [author_mail])
            email.content_subtype = "html"
            email.send()

            return redirect("forumapp:question_details", questID=quest.id)
        
        elif form.is_valid() and stopNotification:
            new_answer = form.save(commit=False)
            new_answer.question = quest
            new_answer.user = request.user
            new_answer.save()

            return redirect("forumapp:question_details", questID=quest.id)

        else:
            messages.error(request,
                           "Something went wrong, data hasn't been saved. Try again!")
            return render(request, "add_answer.html", {"question":quest})

@login_required
def delete_my_item(request, itemID, itemType):
    item_to_remove = get_object_or_404(Question, pk=itemID, user=request.user) if itemType == "question" else get_object_or_404(Answer, pk=itemID, user=request.user)
    item_to_remove.delete()
    return redirect("forumapp:home")

@login_required
def like_dislike_item(request, itemID, itemType):
    item_to_like = get_object_or_404(Question, pk=itemID) if itemType == "question" else get_object_or_404(Answer, pk=itemID)
    isLiked =  item_to_like.likes.filter(id=request.user.id)
    if isLiked:
        item_to_like.likes.remove(request.user)
    else:
        item_to_like.likes.add(request.user)

    if itemType == "question":
        return redirect("forumapp:question_details", questID=item_to_like.id)
    else:
        return redirect("forumapp:question_details", questID=item_to_like.question.id)

@login_required
def display_collection(request, type):
    typeToReturn="questions" if type=="quest" else "answers"
    return render(request, "display_collection.html", {"type":typeToReturn,
                                                       "questions":"questions",
                                                       "answers":"answers"})

def search(request):
    keywords = request.POST.get("search").split(" ")
    for word in keywords:
        queryset = Question.objects.filter(
            Q(title__icontains = word) | 
            Q(text__icontains = word) | 
            Q(user__username__icontains = word) | 
            Q(tags__name__icontains = word)
        )
        try:
            questions = questions | queryset
        except UnboundLocalError:
            questions = queryset
        questions = questions.order_by("-create_date")
        return render(request, "search.html", {"questions":questions})



