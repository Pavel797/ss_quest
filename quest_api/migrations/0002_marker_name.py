# Generated by Django 2.1 on 2018-11-14 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='marker',
            name='name',
            field=models.CharField(default=1, max_length=120),
            preserve_default=False,
        ),
    ]
