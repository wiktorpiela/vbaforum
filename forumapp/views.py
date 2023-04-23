from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm, SendEmailMessageForm
from taggit.models import Tag
from django.contrib import messages
from django.template.defaultfilters import slugify
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

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
        ansYourQuest = True if quest.user == request.user else False

        if form.is_valid() and not stopNotification: #and not ansYourQuest
            new_answer = form.save(commit=False)
            new_answer.question = quest
            new_answer.user = request.user
            new_answer.save()

            author_mail = request.user.email
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
def delete_my_item(request, itemID, itemType, pageLocation):
    item_to_remove = get_object_or_404(Question, pk=itemID, user=request.user)\
          if itemType == "question" else get_object_or_404(Answer, pk=itemID, user=request.user)
    depID = item_to_remove.question.id if itemType != "question" else None
    item_to_remove.delete()
    if itemType == "question":
        if pageLocation=="quest-details":
            return redirect("forumapp:home")
        elif pageLocation=="quest-my":
            # itemsQueryset = Question.objects.filter(user=request.user)
            # return render(request, "display_collection_items.html",
            #               {"items":itemsQueryset,
            #                "itemType":"my",
            #                "type":itemType})
            pass
        elif pageLocation=="quest-fav":
            pass
    else:
        if pageLocation=="quest-details":
            return redirect("forumapp:question_details", questID=depID)
        elif pageLocation=="ans-my":
            pass
        elif pageLocation=="ans-fav":
            pass
                
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
    returnType = "questions" if type == "q" else "answers"
    return render(request, "display_collection.html", {"type":type,
                                                       "returnType":returnType})

@login_required
def display_collection_items(request, type, itemType):

    if type == "questions" and itemType == "my":
        itemsQueryset = Question.objects.filter(user=request.user)

    elif type == "questions" and itemType == "fav":
        itemsQueryset = User.objects.prefetch_related("likes")\
            .get(pk=request.user.id).likes.all()
        
        for item in itemsQueryset:
            if item.user == request.user:
                item.is_your = True
            else:
                item.is_your = False
   
    elif type == "answers" and itemType == "my":
        itemsQueryset = Answer.objects.filter(user=request.user)

    elif type == "answers" and itemType == "fav":
        itemsQueryset = User.objects.prefetch_related("answerLikes")\
            .get(pk=request.user.id).answerLikes.all()
        
        for item in itemsQueryset:
            if item.user == request.user:
                item.is_your = True
            else:
                item.is_your = False

    return render(request, "display_collection_items.html",
                  {"items":itemsQueryset,
                   "itemType":itemType,
                   "type":type})

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
    
@login_required
def edit_item(request, itemID, itemType, pageLocation):

    if itemType == "question":
        item_to_edit = get_object_or_404(Question, pk=itemID, user=request.user)
        item_form = QuestionForm(instance=item_to_edit)
    else:
        item_to_edit = get_object_or_404(Answer, pk=itemID, user=request.user)
        item_form = AnswerForm(instance=item_to_edit)

    if request.method == "GET":
        return render(request, "edit_item.html", {"item":item_to_edit,
                                                  "itemType":itemType,
                                                  "form":item_form,
                                                  "location":pageLocation})
    else:
        editedItem = QuestionForm(request.POST, request.FILES, instance=item_to_edit) \
            if itemType == "question" else AnswerForm(request.POST, request.FILES, instance=item_to_edit)
        
        if editedItem.is_valid():
            editedItem.save()
            if itemType=="question":
                if pageLocation=="quest-details":
                    return redirect("forumapp:question_details", questID=itemID)
                elif pageLocation=="quest-my":
                    return HttpResponseRedirect(reverse("forumapp:display_collection_items", kwargs={"type":"q","itemType":"my"}))
                    # return redirect("forumapp:display_collection_items", type = "q", itemType = "my")
                elif pageLocation=="quest-fav":
                    return redirect("forumapp:display_collection_items", type = "q", itemType = "fav")
            else:
                if pageLocation=="ans-my":
                    return redirect("forumapp:display_collection_items", type = "a", itemType = "my")
                elif pageLocation=="ans-fav":
                    return redirect("forumapp:display_collection_items", type = "a", itemType = "fav")
                elif pageLocation=="quest-details":
                    return redirect("forumapp:question_details", questID=item_to_edit.question.id)
        else:
            messages.error(request, "Something went wrong, data hasn't been saved. Try again!")
            return render(request, "edit_item.html", {"item":item_to_edit,
                                                      "itemType":itemType})
        
def profile_view(request, userID):
    this_user = get_object_or_404(User, pk=userID)
    this_user.is_your_profile = True if request.user == this_user else False
    roles = UserProfile.roles[:-1]  
    return render(request, "forumapp_profile_view.html", 
                  {"userProf":this_user,
                   "roles":roles})

class SendEmailMessageView(LoginRequiredMixin ,TemplateView):
    template_name = "send_email_message.html"
    messageForm = SendEmailMessageForm

    def get(self, request, userID):
        user_receiver =  get_object_or_404(User, pk=userID)
        return render(request, 
                      self.template_name, 
                      {"user_receiver":user_receiver})
    
    def post(self, request, userID):
            message_subject = request.POST.get("subject")
            message = request.POST.get("message")
            attachment = request.FILES.get("attachment")
            user_receiver =  get_object_or_404(User, pk=userID)
            form = SendEmailMessageForm(request.POST, request.FILES)

            if form.is_valid():
                formSaved = form.save(commit=False)
                formSaved.sender = request.user
                formSaved.receiver = user_receiver
                formSaved.save()

                email = EmailMessage(
                    subject=f"VBA Forum on behalf of user: {request.user}",
                    body = f"""
                    <h3>Title: {message_subject}</h3> <br> 
                    {message} <br> 
                    Regards, {request.user}""",
                    from_email= settings.DEFAULT_FROM_EMAIL,
                    to=[user_receiver.email])
                email.content_subtype = "html"
                if attachment:
                    email.attach(attachment.name, attachment.read(), attachment.content_type)
                email.send()
                messages.error(request, "Your email has been sent!")
                return redirect("forumapp:send_email_message", userID=userID)
            else:
                messages.error(request, "Something went worng. No email message sent.")
                return redirect("forumapp:send_email_message",userID=userID)


    



    




