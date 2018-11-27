from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=512)
    uid = models.CharField(max_length=120)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    url_image = models.CharField(max_length=1024)
    standard_of_living = models.IntegerField(default=3)
    count_take_respawn = models.IntegerField(default=0)
    count_jacket = models.IntegerField(default=0)
    count_flamethrower = models.IntegerField(default=0)
    time_contact_marker = models.DateTimeField(default=timezone.now)
    time_kill_zombie = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class MarkerType(models.Model):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class Marker(models.Model):
    name = models.CharField(max_length=512)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    url_image = models.CharField(max_length=1024)
    priority = models.IntegerField(default=0)
    type = models.ForeignKey(MarkerType, on_delete=models.CASCADE, related_name='markers')
    casualty_radius = models.DecimalField(max_digits=9, decimal_places=6)
    key = models.CharField(max_length=120)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='markers', blank=True, null=True)
    team_taken = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='taken_markers', blank=True, null=True)
    time_take = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.type)


class Hint(models.Model):
    read_teams = models.ManyToManyField(Team, blank=True, related_name='read_hint')
    target_teams = models.ManyToManyField(Team, blank=True, related_name='hint')
    hint = models.TextField()

    def __str__(self):
        return self.hint
