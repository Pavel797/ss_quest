# Generated by Django 2.1 on 2018-11-25 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quest_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='count_fail_marker_key',
        ),
    ]
