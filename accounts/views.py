from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from verify_email.email_handler import send_verification_email
from .forms import UserRegistrationForm, UserProfileRegistrationForm
from .models import UserProfile
from .func import validate_email
from django.core.exceptions import ValidationError

def register(request):
    roles = UserProfile.roles[:-1]
    if request.method == "GET":   
        return render(request, "register.html", {"roles":roles})
    else:
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        emailTaken = User.objects.filter(email=email).exists()
        usernameTaken = User.objects.filter(username=username).exists()
        emailValid = validate_email(email)

        if password1==password2:

            try:
                validate_password(password1)
            except ValidationError as exceptions:
                return render(request, "register.html",{"passError":exceptions,
                                                        "length":len(list(exceptions)),
                                                        "roles":roles})
            else:
                if not emailTaken and not usernameTaken and emailValid:
                    form = UserRegistrationForm(request.POST)
                    inactiveUser = send_verification_email(request, form)
                    if inactiveUser:
                        profileForm = UserProfileRegistrationForm(request.POST)
                        profileForm.user = inactiveUser.id
                        profileForm.save()
                        return redirect("accounts:register")
                    
                elif emailTaken and not usernameTaken and emailValid:
                    return render(request, "register.html", {"roles":roles})

        else:
            message = "Passwords don't match! Please try again."
            return render(request, "register.html", {"roles":roles,
                                                     "message":message})
