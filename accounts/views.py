from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from verify_email.email_handler import send_verification_email
from .forms import UserRegistrationForm, UserProfileRegistrationForm, UserForm, UserProfileForm
from .models import UserProfile
from .func import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect 
from django.urls import reverse_lazy

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
                        inactiveUser = send_verification_email(request, userForm)
                        newProfile = profileForm.save(commit=False)
                        newProfile.user = inactiveUser
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
        
def login_user(request):
    if request.method == "GET":
        return render(request, "login_user.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        userExists = User.objects.filter(username=username).exists()
        userIsActive = User.objects.filter(username=username,
                                           is_active=True).exists()
        if userExists and userIsActive:
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                login(request, user)
                return redirect("forumapp:home")
            else:
                messages.error(request, "Wrong credentials! Try again.")
                return render(request, "login_user.html")
        elif not userExists:
            messages.error(request, "This user doesn't exist. Please create account and try again.")
            return render(request, "login_user.html")
        elif not userIsActive:
            messages.error(request, "This user is inactive currently. Activate your account through email and try again.")
            return render(request, "login_user.html")

@login_required       
def logout_user(request):
    logout(request)
    return redirect("forumapp:home")

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile_view.html"
    extra_context = {"roles":UserProfile.roles[:-1]}

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = UserProfileForm
    template_name = "profile_update.html"

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = UserProfileForm(post_data, file_data, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.error(request, 'Your profile is updated successfully!')
            return HttpResponseRedirect(reverse_lazy('accounts:profile_view'))
        
        roles = UserProfile.roles[:-1]
        for short, long in roles:
            if short == request.user.userprofile.role:
                break
        
        context = self.get_context_data(user_form=user_form,
                                        profile_form=profile_form,
                                        roles=roles,
                                        user_current_fullname_role = long,
                                        user_current_short_role = short)
        
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs) 

@login_required  
def remove_account(request):
    userKey = request.user.id
    logout(request)
    User.objects.filter(pk=userKey).delete()
    return redirect("forumapp:home")

        
