# Generated by Django 4.1.7 on 2023-03-28 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('DEV', 'developer'), ('STU', 'student'), ('INT', 'internship'), ('MAN', 'project manager'), ('EMP', 'employer'), ('TEC', 'teacher'), ('OTH', 'other'), ('ADM', 'admin')], default='ADM', max_length=3),
        ),
    ]
