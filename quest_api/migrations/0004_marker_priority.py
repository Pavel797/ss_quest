# Generated by Django 2.1 on 2018-11-14 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_api', '0003_auto_20181114_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='marker',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]