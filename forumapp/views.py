from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer, SendEmailMessage
from accounts.models import UserProfile
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
    quest_posted_count = Question.objects.filter(user=quest.user).count()
    followersCount = quest.user.following.all().count()

    quest.is_your = True if quest.user == request.user else False
    quest.is_liked = True if quest.likes.filter(id=request.user.id).exists() else False

    answers = Answer.objects.filter(question = quest).order_by("-create_date")

    for answer in answers:
        answer.author_followers_count = answer.user.following.all().count()
        answer.answ_posted_count = Question.objects.filter(user = answer.user).count()
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
                                                     "answers":answers,
                                                     "quest_posted_count":quest_posted_count,
                                                     "followersCount":followersCount})

@login_required
def add_answer(request, questID):
    quest = get_object_or_404(Question, pk=questID)
    quest_posted_count = Question.objects.filter(user=quest.user).count()
    if request.method == "GET":
        return render(request, "add_answer.html",{"question":quest,
                                                  "quest_posted_count":quest_posted_count})
    else:
        form = AnswerForm(request.POST, request.FILES)
        stopNotification = quest.user.userprofile.stop_notifications
        ansYourQuest = True if quest.user == request.user else False

        if form.is_valid() and not stopNotification: #and not ansYourQuest
            new_answer = form.save(commit=False)
            new_answer.question = quest
            new_answer.user = request.user
            new_answer.save()

            author = new_answer.user
            quest_author = new_answer.question.user
            email = EmailMessage(
                f"Your question '{quest.title}' has been asnwered by {author.username}",
                f"""Hi, {quest_author}<br>
                {request.user.username} has just added the answer to your question!<br>
                Content of the response:
                {new_answer.text} <br>
                Best regards, VBA forum Team""",
                settings.DEFAULT_FROM_EMAIL,
                [quest_author.email])
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
    item_to_remove = get_object_or_404(Question, pk=itemID, user=request.user)\
          if itemType == "question" else get_object_or_404(Answer, pk=itemID, user=request.user)
    depID = item_to_remove.question if itemType != "question" else None
    item_title = item_to_remove.title if itemType == "question" else None
    item_to_remove.delete()
    if itemType == "question":
        messages.error(request, f"{itemType.capitalize()} '{item_title}' has been successfully deleted.")
        return render(request, "item_action_done.html")
    else:
        messages.error(request, f"{itemType.capitalize()} of question: '{depID.title}' has been successfully deleted.")
        return render(request, "item_action_done.html")
              
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
    if type == "q":
        returnType = "questions"
    elif type=="a":
        returnType = "answers"
    else:
        returnType = "community"
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
        questions = list(set(questions.order_by("-create_date")))
        return render(request, "search.html", {"questions":questions})
    
@login_required
def edit_item(request, itemID, itemType):

    if itemType == "question":
        item_to_edit = get_object_or_404(Question, pk=itemID, user=request.user)
        item_form = QuestionForm(instance=item_to_edit)
    else:
        item_to_edit = get_object_or_404(Answer, pk=itemID, user=request.user)
        item_form = AnswerForm(instance=item_to_edit)

    if request.method == "GET":
        return render(request, "edit_item.html", {"item":item_to_edit,
                                                  "itemType":itemType,
                                                  "form":item_form})
    else:
        editedItem = QuestionForm(request.POST, request.FILES, instance=item_to_edit) \
            if itemType == "question" else AnswerForm(request.POST, request.FILES, instance=item_to_edit)
        
        if editedItem.is_valid():
            editedItem.save()

            if itemType=="question":
                messages.error(request, f"{itemType.capitalize()} '{item_to_edit.title}' has been successfully modified! ")
                return render(request, "item_action_done.html")
            else:
                messages.error(request, f"{itemType.capitalize()} of question '{item_to_edit.question.title}' has been successfully modified! ")
                return render(request, "item_action_done.html")
        else:
            messages.error(request, "Something went wrong, data hasn't been saved. Try again!")
            return render(request, "edit_item.html", {"item":item_to_edit,
                                                      "itemType":itemType})
        
def profile_view(request, userID):
    this_user = get_object_or_404(User, pk=userID)
    this_user.is_your_profile = True if request.user == this_user else False
    roles = UserProfile.roles[:-1]
    quest_posted_count = Question.objects.filter(user=this_user).count()
    followersCount = this_user.following.all().count() #third column of manytomanyfield table 
    isFollowed = this_user.following.filter(user_id=request.user.id).exists()
    if isFollowed:
        this_user.is_followed = True
    else:
        this_user.is_followed = False

    return render(request, 
                  "forumapp_profile_view.html", 
                  {"userProf":this_user,
                   "roles":roles,
                   "quest_posted_count":quest_posted_count,
                   "followersCount":followersCount})

class SendEmailMessageView(LoginRequiredMixin, TemplateView):
    template_name = "send_email_message.html"
    messageForm = SendEmailMessageForm

    def get(self, request, userID):
        user_receiver =  get_object_or_404(User, pk=userID)
        roles = UserProfile.roles
        all_messages = SendEmailMessage.objects.filter(
            (Q(receiver=request.user) | Q(sender=request.user)) &
            (Q(receiver=userID) | Q(sender=userID))
            ).order_by("message_date")
    
        for message in all_messages:
            if message.sender == request.user:
                message.are_you_sender = True
            else:
                message.are_you_sender = False

        return render(request, 
                      self.template_name, 
                      {"user_receiver":user_receiver,
                       "roles":roles,
                       "all_messages":all_messages})
    
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
            
@login_required
def display_my_conversations(request):
    roles = UserProfile.roles
    #wybierz takie wiadomosci w ktorych jestem nadawca lub odbiorca
    userAssociatedMessages = SendEmailMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    #wez takie unikalne id userów z ktorymi miałem wiadomości (nie moje id)
    receivers = list(userAssociatedMessages.values_list("receiver").distinct())
    senders = list(userAssociatedMessages.values_list("sender").distinct())
    receivers_list = []
    sender_list = []
    for x in range(len(receivers)):
        receivers_list.append(receivers[x][0])
    for x in range(len(senders)):
        sender_list.append(senders[x][0])

    allIds = receivers_list + sender_list
    allContacts =[]
    for id in allIds:
        if id != request.user.id and id not in allContacts:
            allContacts.append(id)

    # contacts_coversations = User.objects.filter(id__in=allContacts)

    #dlugosci konwersjacji dla tych uzytkowników
    convLength = []
    for contanct in allContacts:
        conv_len = userAssociatedMessages.filter(Q(sender=contanct) | Q(receiver=contanct)).count()
        convLength.append(conv_len)

    users=[]
    for contactID in allContacts:
        tempUser = User.objects.get(pk=contactID)
        users.append(tempUser)

    convContactLength = list(zip(users, convLength))

    return render(request, 
                  "display_my_conversations.html",
                  {"convContactAndLength":convContactLength,
                   "roles":roles})

@login_required
def conversation_details(request, userContactID):
    roles = UserProfile.roles
    userContact = get_object_or_404(User, pk=userContactID)
    all_messages = SendEmailMessage.objects.filter(
        (Q(receiver=request.user) | Q(sender=request.user)) &
        (Q(receiver=userContactID) | Q(sender=userContactID))
        ).order_by("message_date")
    
    for message in all_messages:
        if message.sender == request.user:
            message.are_you_sender = True
        else:
            message.are_you_sender = False

    return render(request, 
                  "conversation_details.html",
                  {"all_messages":all_messages,
                   "userContact":userContact,
                   "roles":roles})

@login_required
def all_users(request):
    all_active_users = User.objects.filter(Q(is_active = True) & Q(is_staff = False)).all()
    roles = UserProfile.roles
    return render(request, "all_users.html",
                  {"all_active_users":all_active_users,
                   "roles":roles})

@login_required
def browse_users(request):
    keywords = request.POST.get("browse_users").split(" ")
    roles = UserProfile.roles[:-1]

    # long = []
    # short = []

    # for role in roles:
    #     short.append(role[0])
    #     long.append(role[1])

    for word in keywords:
        queryset = User.objects.filter(
            (Q(is_active = True) & Q(is_staff = False)) &
            (Q(username__icontains = word) | 
            Q(userprofile__role__icontains = word)) 
            )
        try:
            questions = questions | queryset
        except UnboundLocalError:
            questions = queryset
        questions = questions.all()
        return render(request, "browse_users.html",
                      {"found_users":questions,
                       "roles":roles})
    
@login_required
def reply_to_message(request, userContactID, messageID):
    userContact = get_object_or_404(User, pk=userContactID)
    messageTo = get_object_or_404(SendEmailMessage, pk=messageID)

    if request.method == "GET":
        return render(request, "reply_to_message.html",
                      {"userContact":userContact,
                       "messageTo":messageTo})
    
    else:
        message_subject = request.POST.get("subject")
        message = request.POST.get("message")
        attachment = request.FILES.get("attachment")
        form = SendEmailMessageForm(request.POST, request.FILES)

        if form.is_valid():
            formSaved = form.save(commit=False)
            formSaved.sender = request.user
            formSaved.receiver = userContact
            formSaved.save()

            email = EmailMessage(
                subject=f"VBA Forum on behalf of user: {request.user}",
                body = f"""
                <h3>Title: {message_subject}</h3> <br> 
                {message} <br> 
                Regards, {request.user}""",
                from_email= settings.DEFAULT_FROM_EMAIL,
                to=[userContact.email])
            email.content_subtype = "html"
            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)
            email.send()
            messages.error(request, "Your email has been sent!")
            return redirect("forumapp:conversation_details", userContactID=userContactID)
        else:
            messages.error(request, "Something went worng. No email message sent.")
            return redirect("forumapp:conversation_details",userContactID=userContactID)
        
@login_required
def follow_unfollow(request, followingUserID):
    userToFollow = User.objects.get(id=followingUserID)
    userFollower = UserProfile.objects.get(user_id=request.user)
    isFollowed = userToFollow.following.filter(user_id=userFollower.user.id).exists()
    
    if isFollowed:
        userToFollow.following.remove(userFollower)
    else:
        userToFollow.following.add(userFollower)

    return redirect("forumapp:profile_view", userID=followingUserID)

@login_required
def my_contacts(request):
    followingUsers = UserProfile.objects.prefetch_related("following")\
        .get(pk=request.user.id).following.order_by("username")
    roles = UserProfile.roles
    return render(request,
                  "my_contacts.html",
                  {"followingUsers":followingUsers,
                   "roles":roles})


    



    



    



    




