from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import *


def get_markers(request):
    message = 'markers received'

    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'

    makers = Marker.objects.filter(Q(team__uid=uid_team) | Q(is_public=True)) \
        .filter(team_taken=None).all()

    data = [{
        'id': maker.id,
        'longitude': maker.longitude,
        'latitude': maker.latitude,
        'url':'https://img-fotki.yandex.ru/get/195853/200418627.1a7/0_18d5d6_9a3b2bed_orig.png',
        'is_public': maker.is_public
    } for maker in makers]

    return JsonResponse({
        'success': 1,
        'message': message,
        'data': data
    })


def take_marker(request):
    message = 'marker taken'
    result = 1

    key_marker = request.GET.get('key_marker')
    uid_team = request.GET.get('uid_team')

    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'
        result = 0

    if not key_marker:
        message = 'marker key is invalid'
        result = 0

    marker = None
    if result:
        marker = Marker.objects.filter(key=key_marker) \
            .filter(Q(team__uid=team.uid) | Q(is_public=True)).first()

    if result and marker and marker.team_taken:
        message = 'marker already taken'
        result = 0

    if result and marker:
        marker.team_taken = team
        marker.save()
        result = 1
    elif result:
        message = 'marker not found'
        result = 0

    return JsonResponse({
        'success': 1,
        'message': message,
        'data': {
            'result': result
        }

    })


def get_hints(request):
    message = 'hints received'

    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'

    hints = Hint.objects.filter(read_teams__uid__exact=team.uid).exclude()

    data = [{
        'id': hint.id,
        'hint': hint.hint
    } for hint in hints]

    return JsonResponse({
        'success': 1,
        'message': message,
        'data': data
    })
