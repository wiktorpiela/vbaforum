# Generated by Django 4.1.7 on 2023-04-22 20:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forumapp', '0004_sendemailmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendemailmessage',
            name='message_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]