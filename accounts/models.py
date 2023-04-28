from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key = True)
    
    bio = models.TextField(max_length=500, blank=True)
    
    roles = [
        ("DEV", "developer"),
        ("STU", "student"),
        ("INT", "internship"),
        ("MAN", "project manager"),
        ("EMP", "employer"),
        ("TEC", "teacher"),
        ("OTH", "other"),
        ("ADM", "admin"),
    ]

    role = models.CharField(
        max_length=3,
        choices=roles,
        default="ADM"
    )

    avatar = models.ImageField(upload_to="images/", default="images/default_user_img.jpg")

    stop_notifications = models.BooleanField(default=False,
                                             help_text= "if user wants to turn off email notification when question has been answered")
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

    def __str__(self):
        return f"{self.user}"
    
    def display_fullname_user_role(self):
        for short, long in self.roles:
            if self.role == short:
                return long


