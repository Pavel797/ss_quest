from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import *


def get_markers(request):
    message = 'markers received'
    result = 1

    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'
        result = 0

    data = []
    if result:
        makers = Marker.objects.filter(Q(team__uid=uid_team) | Q(is_public=True)) \
                     .filter(team_taken=None).order_by('-priority')[:3]

        data = [{
            'id': maker.id,
            'name': maker.name,
            'longitude': maker.longitude,
            'latitude': maker.latitude,
            'url': maker.url_image,
            'is_public': maker.is_public
        } for maker in makers]

    return JsonResponse({
        'success': result,
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
        team.count_fail_marker_key += 1
        team.save()

    return JsonResponse({
        'success': 1,
        'message': message,
        'data': {
            'result': result
        }

    })


def get_hints(request):
    message = 'hints received'
    result = 1

    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'
        result = 0

    hints = None
    if result:
        hints = Hint.objects.filter(target_teams__exact=team).exclude(read_teams__exact=team)
    if hints and result:
        for hint in hints:
            hint.read_teams.add(team)
            hint.save()

    data = []
    if result:
        data = [{
            'id': hint.id,
            'hint': hint.hint
        } for hint in hints]

    return JsonResponse({
        'success': result,
        'message': message,
        'data': data
    })


def set_my_position(request):
    message = 'position is set'
    result = 1

    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        message = 'team not found'
        result = 0

    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    if not latitude or not longitude or \
            not latitude.isdigit() or not longitude.isdigit():
        message = 'no data available'
        result = 0

    if result:
        team.latitude = float(latitude)
        team.longitude = float(longitude)
        team.save()

    return JsonResponse({
        'success': result,
        'message': message
    })
