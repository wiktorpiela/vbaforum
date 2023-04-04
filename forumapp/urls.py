from django.urls import path
from . import views

app_name = "forumapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("new-question/", views.new_question, name="new_question"),
    path("question-details/<int:questID>/", views.question_details, name="question_details"),
    path("display-collection/<str:type>/", views.display_collection, name="display_collection"),
    
]