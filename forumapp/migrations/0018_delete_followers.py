# Generated by Django 4.1.7 on 2023-04-28 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forumapp', '0017_rename_who_is_following_followers_another_user_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Followers',
        ),
    ]