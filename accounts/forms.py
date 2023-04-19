from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django import forms

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username","email","password1","password2",)

class UserProfileRegistrationForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ("role",)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",
                  "email",
                  )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("bio",
                  "role",
                  "avatar",
                  "stop_notifications")

