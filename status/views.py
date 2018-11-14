from django.shortcuts import render
from django.http import HttpResponse
from quest_api.models import *


def index(request):
    markers = Marker.objects.all()
    teams = Team.objects.all()

    return render(request, 'status/index.html', {
        'teams': teams,
        'markers': markers,
        'centerMap': '[54.333064, 48.385672]'
    })
