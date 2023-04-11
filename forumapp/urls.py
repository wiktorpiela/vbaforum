from django.urls import path
from . import views

app_name = "forumapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("new-question/", views.new_question, name="new_question"),
    path("question-details/<int:questID>/", views.question_details, name="question_details"),
    path("display-collection/<str:type>/", views.display_collection, name="display_collection"),
    path("add-answer/<int:questID>/", views.add_answer, name="add_answer"),
    path("delete-my-item/<int:itemID>/<str:itemType>/", views.delete_my_item, name="delete_my_item"),
    path("like-dislike-item/<int:itemID>/<str:itemType>/", views.like_dislike_item, name="like_dislike_item"),
    path("search-item/", views.search, name="search"),

    
]