# Generated by Django 4.1.7 on 2023-04-28 06:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forumapp', '0015_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followers',
            name='who_follows_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='who_follows', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='followers',
            name='who_is_following',
        ),
        migrations.AddField(
            model_name='followers',
            name='who_is_following',
            field=models.ManyToManyField(related_name='who_is_following', to=settings.AUTH_USER_MODEL),
        ),
    ]
