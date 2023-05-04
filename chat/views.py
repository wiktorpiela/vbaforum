from django.shortcuts import render, get_object_or_404
from .models import Room, Message
from django.contrib.auth.decorators import login_required

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
