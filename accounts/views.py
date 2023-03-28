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
from django.contrib import messages

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
                    userForm = UserRegistrationForm(request.POST)
                    profileForm = UserProfileRegistrationForm(request.POST)
                    if userForm.is_valid() and profileForm.is_valid():
                        send_verification_email(request, userForm)
                        newUser = userForm.save()
                        newProfile = profileForm.save(commit=False)
                        newProfile.user = newUser
                        newProfile.save()
                        messages.success(request, """
                            Your account has been successfully created.
                            Please check your mailbox to activate this account.
                            """)
                        return redirect("accounts:register")
                    else:
                        error = "Something went wrog. Please try again."
                        return render(request, "register.html", {"roles":roles,
                                                                 "error":error})
                    
                elif emailTaken:
                    error = "This email is already taken! Please try again."
                    return render(request, "register.html", {"roles":roles,
                                                             "error":error})
                elif usernameTaken:
                    error = "This username is already taken! Please try again."
                    return render(request, "register.html", {"roles":roles,
                                                             "error":error})
                elif not emailValid:
                    error = "Wrong email format!  Please try again."
                    return render(request, "register.html", {"roles":roles,
                                                             "error":error})

        else:
            error = "Passwords don't match! Please try again."
            return render(request, "register.html", {"roles":roles,
                                                     "error":error})
