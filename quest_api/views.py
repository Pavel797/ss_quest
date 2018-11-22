from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import *
from math import *
import time

"""

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker-compose -f docker-compose.staging.yml up -d

"""


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

    if result and team.standard_of_living <= 0:
        message = 'no lives.'
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

        if marker.type.name == 'flamethrower':
            team.count_flamethrower += 1
        elif marker.type.name == 'jacket':
            team.count_jacket += 1

        marker.save()
        result = 1
    elif result:
        message = 'marker not found'
        result = 0
        team.count_fail_marker_key += 1
        team.save()

    return JsonResponse({
        'success': result,
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
            not isfloat(latitude) or not isfloat(longitude):
        message = 'no data available'
        result = 0

    if result:
        team.latitude = float(latitude)
        team.longitude = float(longitude)

        markers = Marker.objects.all()

        for marker in markers:
            if marker.type == 'zombie' and team.standard_of_living > 0 and \
                    haversine(team.latitude, team.longitude, marker.latitude,
                              marker.longitude) < marker.casualty_radius:
                if team.count_flamethrower > 0:
                    team.count_flamethrower -= 1
                    marker.team_taken = team
                elif team.count_jacket > 0:
                    team.count_jacket -= 1
                    team.time_contact_marker = time.time()
                elif (time.time() - team.time_contact_marker) > 60:
                    team.time_contact_marker = time.time()
                    team.standard_of_living -= 1
                break
            elif marker.type == 'respawn' and haversine(team.latitude, team.longitude, marker.latitude,
                                                        marker.longitude) < marker.casualty_radius and team.standard_of_living <= 0:
                team.standard_of_living = 3
                break

            team.save()

        return JsonResponse({
            'success': result,
            'message': message
        })
