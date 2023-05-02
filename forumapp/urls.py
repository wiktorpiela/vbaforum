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
    path("display-collection/<str:type>/items/<str:itemType>/", views.display_collection_items, name="display_collection_items"),
    path("edit-item/<int:itemID>/<str:itemType>/", views.edit_item, name="edit_item"),
    path("profile-view/<int:userID>/", views.profile_view, name="profile_view"),
    path("send-email-message/<int:userID>/", views.SendEmailMessageView.as_view(), name="send_email_message"),
    path("display-my-conversations", views.display_my_conversations, name="display_my_conversations"),
    path("conversation-details/<int:userContactID>/", views.conversation_details, name="conversation_details"),
    path("all-users/", views.all_users, name="all_users"),
    path("browse-users/", views.browse_users, name="browse_users"),
    path("reply_to_message/<int:userContactID>/<int:messageID>/", views.reply_to_message, name="reply_to_message"),
    path("follow-unfollow/<int:followingUserID>/", views.follow_unfollow, name="follow_unfollow"),
    path("my-contacts/", views.my_contacts, name="my_contacts"),
]