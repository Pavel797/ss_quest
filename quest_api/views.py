from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from .models import *
from math import *
import time

"""

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker-compose -f docker-compose.staging.yml up -d

"""


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    met = 6356863 * c
    return met


def create_base_json_response(result_code, message, data=None):
    return JsonResponse({
        'success': result_code,
        'message': message,
        'data': data
    })


def get_markers(request):
    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        return create_base_json_response(0, 'team not found')

    if team.standard_of_living > 0:
        makers = Marker.objects.filter(Q(team__uid=uid_team) | Q(is_public=True)) \
                     .filter(team_taken=None).order_by('-priority')[:3]
    else:
        makers = Marker.objects.filter(type__name='respawn')

    data = [{
        'id': maker.id,
        'name': maker.name,
        'longitude': maker.longitude,
        'latitude': maker.latitude,
        'type': maker.type.name,
        'casualty_radius': maker.casualty_radius
        if maker.type.name == 'zombie' or maker.type.name == 'respawn' else None,
        'url': maker.url_image,
        'is_public': maker.is_public
    } for maker in makers]

    return JsonResponse({
        'success': 1,
        'message': 'markers received',
        'data': data
    })


def take_marker(request):
    key_marker = request.GET.get('key_marker')
    uid_team = request.GET.get('uid_team')

    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        return create_base_json_response(0, 'team not found')

    if team.standard_of_living <= 0:
        return create_base_json_response(0, 'no lives')

    if not key_marker:
        return create_base_json_response(0, 'marker key is invalid')

    marker = Marker.objects.filter(key=key_marker) \
        .filter(Q(team__uid=team.uid) | Q(is_public=True)) \
        .filter(Q(type__name='flamethrower') | Q(type__name='jacket')).first()

    if marker and marker.team_taken:
        return create_base_json_response(0, 'marker already taken')

    if marker:
        marker.team_taken = team

        if marker.type.name == 'flamethrower':
            team.count_flamethrower += 2
        elif marker.type.name == 'jacket':
            team.count_jacket += 1

        marker.save()
        result = 1
    else:
        team.standard_of_living -= 1
        team.save()
        return create_base_json_response(0, 'marker not found')

    return JsonResponse({
        'success': 1,
        'message': 'marker taken',
        'data': {
            'result': result
        }

    })


def get_hints(request):
    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        return create_base_json_response(0, 'team not found')

    hints = Hint.objects.filter(target_teams__exact=team).exclude(read_teams__exact=team)
    if hints:
        for hint in hints:
            hint.read_teams.add(team)
            hint.save()

    data = [{
        'id': hint.id,
        'hint': hint.hint
    } for hint in hints]

    return JsonResponse({
        'success': 1,
        'message': 'hints received',
        'data': data
    })


def set_my_position(request):
    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        return create_base_json_response(0, 'team not found')

    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    if not latitude or not longitude or \
            not isfloat(latitude) or not isfloat(longitude):
        return create_base_json_response(0, 'no data available')

    team.latitude = float(latitude)
    team.longitude = float(longitude)

    markers = Marker.objects.all()

    for marker in markers:
        distance =  haversine(team.latitude, team.longitude, marker.latitude, marker.longitude)
        if marker.type.name == 'respawn' and distance <= marker.casualty_radius:
            team.standard_of_living = 3
            team.count_take_respawn += 1
            break
        elif marker.type.name == 'zombie' and team.standard_of_living > 0 and distance <= marker.casualty_radius:
            if team.count_jacket > 0:
                team.count_jacket -= 1
                team.time_contact_marker = datetime.now()
            elif (time.time() - team.time_contact_marker.timestamp()) > 60:
                team.time_contact_marker = datetime.now()
                team.standard_of_living -= 1

            if team.count_flamethrower > 0:
                team.count_flamethrower -= 1
                marker.team_taken = team
                marker.save()
            break

    team.save()

    return JsonResponse({
        'success': 1,
        'message': 'position is set',
        'data': {
            'count_lives': team.standard_of_living,
            'count_flamethrower': team.count_flamethrower,
            'count_jacket': team.count_jacket
        }
    })
