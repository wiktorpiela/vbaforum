# Generated by Django 4.1.7 on 2023-04-23 07:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forumapp', '0006_delete_sendemailmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='SendEmailMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('attachment', models.ImageField(blank=True, upload_to='')),
                ('message_date', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userReceiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userSender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]