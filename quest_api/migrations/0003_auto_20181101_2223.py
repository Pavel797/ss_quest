# Generated by Django 2.1.3 on 2018-11-01 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quest_api', '0002_auto_20181101_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marker',
            name='team_taken',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quest_api.Team'),
        ),
    ]
