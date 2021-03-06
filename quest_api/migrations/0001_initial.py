# Generated by Django 2.1 on 2018-11-27 14:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


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
                ('name', models.CharField(max_length=512)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('url_image', models.CharField(max_length=1024)),
                ('priority', models.IntegerField(default=0)),
                ('casualty_radius', models.DecimalField(decimal_places=6, max_digits=9)),
                ('key', models.CharField(max_length=120)),
                ('time_take', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MarkerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('uid', models.CharField(max_length=120)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('url_image', models.CharField(max_length=1024)),
                ('standard_of_living', models.IntegerField(default=3)),
                ('count_take_respawn', models.IntegerField(default=0)),
                ('count_jacket', models.IntegerField(default=0)),
                ('count_flamethrower', models.IntegerField(default=0)),
                ('time_contact_marker', models.DateTimeField(default=django.utils.timezone.now)),
                ('time_kill_zombie', models.DateTimeField(default=django.utils.timezone.now)),
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
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taken_markers', to='quest_api.Team'),
        ),
        migrations.AddField(
            model_name='marker',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markers', to='quest_api.MarkerType'),
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
