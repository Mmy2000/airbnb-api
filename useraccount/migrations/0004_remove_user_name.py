# Generated by Django 4.2.16 on 2024-09-27 21:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('useraccount', '0003_profile_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
    ]
