from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login-user/", views.login_user, name="login_user"),
    path("logout-user/", views.logout_user, name="logout_user"),
    path("userprofile/", views.ProfileView.as_view(), name="profile_view"),
    path("userprofile-update/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("remove-account/", views.remove_account, name="remove_account"),
    path("change-user-password/", views.ChangeUserPasswordView.as_view(), name="change_user_password"),
    path("reset-user-password/", views.ResetUserPasswordViewSendRequest.as_view(), name="reset_user_password"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="set_new_user_password.html"), name="reset_user_password_confirm"),


]