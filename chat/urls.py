from django.urls import path
from .import views

app_name = "chat"

urlpatterns = [
    path("rooms/", views.rooms, name="rooms"),
    path("chatroom/<slug:slug>/", views.room, name="room"),
    path("create-new-chatroom-request/", views.send_create_room_request, name="send_create_room_request"),
]