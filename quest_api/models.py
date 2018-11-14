from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=512)
    uid = models.CharField(max_length=120)
    count_fail_marker_key = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Marker(models.Model):
    name = models.CharField(max_length=512)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    url_image = models.CharField(max_length=1024)
    is_public = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    key = models.CharField(max_length=120)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='markers', blank=True, null=True)
    team_taken = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='taken_markers', blank=True, null=True)

    def __str__(self):
        return self.name


class Hint(models.Model):
    read_teams = models.ManyToManyField(Team, blank=True,  related_name='read_hint')
    target_teams = models.ManyToManyField(Team, blank=True, related_name='hint')
    hint = models.TextField()

    def __str__(self):
        return self.hint