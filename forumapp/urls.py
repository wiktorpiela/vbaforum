from django.urls import path
from . import views

app_name = "forumapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("new-question/", views.new_question, name="new_question"),
    
]