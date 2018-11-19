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
    teams = Team.objects.all().values()
    return JsonResponse({
        'markers': list(markers),
        'teams': list(teams)
    })
