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
    markers = Marker.objects.all().values()
    teams = Team.objects.all()

    return JsonResponse({
        'markers': list(markers),
        'teams': [{
            'name': team.name,
            'latitude': team.latitude,
            'url_image': team.url_image,
            'longitude': team.longitude,
            'taken_markers_count': team.taken_markers.count(),
            'count_take_respawn': team.count_take_respawn,
            'standard_of_living': team.standard_of_living
        } for team in teams]
    })
