# Generated by Django 4.1.7 on 2023-04-28 06:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forumapp', '0014_delete_followers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who_follows_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='who_follows', to=settings.AUTH_USER_MODEL)),
                ('who_is_following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='who_is_following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
