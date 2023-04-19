from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login-user/", views.login_user, name="login_user"),
    path("logout-user/", views.logout_user, name="logout_user"),
    path("userprofile/", views.ProfileView.as_view(), name="profile_view"),
    path("userprofile-update/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("remove-account/", views.remove_account, name="remove_account"),
    
]