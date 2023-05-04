from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Message
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages

@login_required
def rooms(request):
    rooms = Room.objects.all()
    return render(request,
                  "rooms.html",
                  {"rooms":rooms})

@login_required
def room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    messages = Message.objects.filter(room=room)[0:25]
    return render(request,
                "room.html",
                {"room":room,
                 "messages":messages})

@login_required
def send_create_room_request(request):
    if request.method == "GET":
        return render(request,
                      "send_create_room_request.html")
    else:
        subject = request.POST.get("request_subject")
        message_body = request.POST.get("request_message")
        if subject and message_body:
            request_autor_email = request.user.email
            email = EmailMessage(
                f"{subject}",
                f"""{message_body} <br>
                Best regards, {request.user.username}""",
                request_autor_email,
                [settings.DEFAULT_FROM_EMAIL])
            email.content_subtype = "html"
            email.send()
            messages.error(request, "Your request has been successfully sent to admin!")
            return redirect("chat:send_create_room_request")
        else:
            messages.error(request, "Something went wrong, no message sent. Please try again!")
            return redirect("chat:send_create_room_request")
