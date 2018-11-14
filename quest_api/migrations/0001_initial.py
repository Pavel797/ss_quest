# Generated by Django 2.1 on 2018-11-14 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hint', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('url_image', models.CharField(max_length=1024)),
                ('is_public', models.BooleanField(default=False)),
                ('key', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=120)),
                ('count_fail_marker_key', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='marker',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='markers', to='quest_api.Team'),
        ),
        migrations.AddField(
            model_name='marker',
            name='team_taken',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quest_api.Team'),
        ),
        migrations.AddField(
            model_name='hint',
            name='read_teams',
            field=models.ManyToManyField(blank=True, related_name='read_hint', to='quest_api.Team'),
        ),
        migrations.AddField(
            model_name='hint',
            name='target_teams',
            field=models.ManyToManyField(blank=True, related_name='hint', to='quest_api.Team'),
        ),
    ]
