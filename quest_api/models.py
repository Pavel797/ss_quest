from django.db import models


class Team(models.Model):
    uid = models.CharField(max_length=120)

    def __str__(self):
        return self.uid


class Marker(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_public = models.BooleanField(default=False)
    key = models.CharField(max_length=120)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='markers', blank=True, null=True)
    team_taken = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.key


class Hint(models.Model):
    read_teams = models.ManyToManyField(Team, blank=True, null=True)
    hint = models.TextField()

    def __str__(self):
        return self.hint