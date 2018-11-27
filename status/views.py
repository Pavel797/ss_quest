from django.shortcuts import render
from django.http import JsonResponse
from quest_api.models import *


def index(request):
    markers = Marker.objects.all()
    teams = Team.objects.all()
    return render(request, 'status/index.html', {
        'teams': teams,
        'markers': markers,
        'centerMap': '[54.333064, 48.385672]'
    })


def get_status_json(request):
    markers = Marker.objects.exclude(type__name='zombie', team_taken__isnull=False).values()
    teams = sorted(Team.objects.all(), key = lambda team: (-team.taken_markers.count(),
                                                          (team.count_take_respawn * 10) +
                                                           team.time_kill_zombie.timestamp()))

    return JsonResponse({
        'markers': list(markers),
        'teams': [{
            'name': team.name,
            'latitude': team.latitude,
            'url_image': team.url_image,
            'longitude': team.longitude,
            'taken_markers_count': Marker.objects.filter(team_taken=team, type__name='zombie').count(),
            'time_kill': team.time_kill_zombie.timestamp(),
            'penalty_time': team.count_take_respawn * 10,
            'standard_of_living': team.standard_of_living
        } for team in teams]
    })
