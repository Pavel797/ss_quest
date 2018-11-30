from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from .models import *
from math import *
import random
import time

"""

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker-compose -f docker-compose.staging.yml up -d

"""

MAX_COUNT_VISIBLE_ZOMBIE = 10
MAX_COUNT_VISIBLE_FLAMETHROWER = 3
MAX_COUNT_VISIBLE_JACKET = 3
TIME_INVULNERABILITY = 15  # sec
MAX_COUNT_LIVES = 3


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


def rewrite_flamethrowers(team, count):
    flamethrowers = Marker.objects.filter(team=team, team_taken__isnull=False, type__name='flamethrower') \
                        .order_by('time_take')[:count]

    if len(flamethrowers) < count:
        print("ERROR")
        return

    for flamethrower in flamethrowers:
        flamethrower.team_taken = None
        flamethrower.save()


def rewrite_jackets(team, count):
    jackets = Marker.objects.filter(team=team, team_taken__isnull=False, type__name='jacket') \
                  .order_by('time_take')[:count]

    if len(jackets) < count:
        print("ERROR")
        return

    for jacket in jackets:
        jacket.team_taken = None
        jacket.save()


def drop_markers(request):
    markers = Marker.objects.all()

    for marker in markers:
        marker.team_taken = None
        marker.save()

    return JsonResponse({
        'success': 1,
        'message': "drop markers"
    })


def get_markers(request):
    uid_team = request.GET.get('uid_team')
    team = Team.objects.filter(uid=uid_team).first()

    if not uid_team or not team:
        return create_base_json_response(0, 'team not found')

    respawns = Marker.objects.filter(type__name='respawn')
    zombies = []
    flamethrowers = []
    jackets = []

    if team.standard_of_living > 0:
        zombies = Marker.objects.filter(team_taken=None, type__name='zombie') \
                      .order_by('-priority')[:MAX_COUNT_VISIBLE_ZOMBIE]

        flamethrowers = Marker.objects.filter(team=team, team_taken__isnull=True, type__name='flamethrower') \
                            .order_by('-priority')[:MAX_COUNT_VISIBLE_FLAMETHROWER]

        jackets = Marker.objects.filter(team=team, team_taken__isnull=True, type__name='jacket') \
                      .order_by('-priority')[:MAX_COUNT_VISIBLE_JACKET]

    if len(flamethrowers) < MAX_COUNT_VISIBLE_FLAMETHROWER:
        rewrite_flamethrowers(team, MAX_COUNT_VISIBLE_FLAMETHROWER - len(flamethrowers))

    if len(jackets) < MAX_COUNT_VISIBLE_JACKET:
        rewrite_jackets(team, MAX_COUNT_VISIBLE_JACKET - len(jackets))

    data = []

    for marker in respawns:
        data.append({
            'id': marker.id,
            'name': marker.name,
            'longitude': marker.longitude,
            'latitude': marker.latitude,
            'type': marker.type.name,
            'casualty_radius': marker.casualty_radius
            if marker.type.name == 'zombie' or marker.type.name == 'respawn' else None,
            'url': marker.url_image,
        })

    for marker in zombies:
        data.append({
            'id': marker.id,
            'name': marker.name,
            'longitude': marker.longitude,
            'latitude': marker.latitude,
            'type': marker.type.name,
            'casualty_radius': marker.casualty_radius
            if marker.type.name == 'zombie' or marker.type.name == 'respawn' else None,
            'url': marker.url_image,
        })

    for marker in flamethrowers:
        data.append({
            'id': marker.id,
            'name': marker.name,
            'longitude': marker.longitude,
            'latitude': marker.latitude,
            'type': marker.type.name,
            'casualty_radius': marker.casualty_radius
            if marker.type.name == 'zombie' or marker.type.name == 'respawn' else None,
            'url': marker.url_image
        })

    for marker in jackets:
        data.append({
            'id': marker.id,
            'name': marker.name,
            'longitude': marker.longitude,
            'latitude': marker.latitude,
            'type': marker.type.name,
            'casualty_radius': marker.casualty_radius
            if marker.type.name == 'zombie' or marker.type.name == 'respawn' else None,
            'url': marker.url_image
        })

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

    flamethrowers = Marker.objects.filter(team=team, team_taken__isnull=True, type__name='flamethrower') \
                        .order_by('-priority')[:MAX_COUNT_VISIBLE_FLAMETHROWER]

    jackets = Marker.objects.filter(team=team, team_taken__isnull=True, type__name='jacket') \
                  .order_by('-priority')[:MAX_COUNT_VISIBLE_JACKET]

    marker = None
    for m in flamethrowers:
        if m.key == key_marker:
            marker = m
            break

    for m in jackets:
        if m.key == key_marker:
            marker = m
            break

    if marker and marker.team_taken:
        team.standard_of_living -= 1
        return create_base_json_response(0, 'marker already taken')

    if not marker:
        team.standard_of_living -= 1

        if team.standard_of_living <= 0:
            team.count_flamethrower = 0
            team.count_jacket = 0

        team.save()
        return create_base_json_response(0, 'marker not found')

    marker.team_taken = team
    marker.time_take = datetime.now()
    if marker.type.name == 'flamethrower':
        team.count_flamethrower += 2
    elif marker.type.name == 'jacket':
        team.count_jacket += 1

    marker.save()
    team.save()

    return JsonResponse({
        'success': 1,
        'message': 'marker taken',
        'data': {
            'result': 1
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
        if marker.team_taken:
            continue

        distance = haversine(team.latitude, team.longitude, marker.latitude, marker.longitude)
        if marker.type.name == 'respawn' and distance <= marker.casualty_radius and team.standard_of_living < MAX_COUNT_LIVES:
            team.standard_of_living = MAX_COUNT_LIVES
            team.count_take_respawn += 1
            break
        elif marker.type.name == 'zombie' and team.standard_of_living > 0 and distance <= marker.casualty_radius:
            if team.count_jacket > 0:
                team.count_jacket -= 1
                team.time_contact_marker = datetime.now()
            elif (time.time() - team.time_contact_marker.timestamp()) > TIME_INVULNERABILITY:
                team.time_contact_marker = datetime.now()
                team.standard_of_living -= 1

            if team.standard_of_living <= 0:
                team.count_flamethrower = 0
                team.count_jacket = 0

            if team.count_flamethrower > 0:
                team.count_flamethrower -= 1
                team.time_kill_zombie = datetime.now()
                marker.team_taken = team
                marker.save()
            break

    team.save()

    count_kills = Marker.objects.filter(team_taken=team, type__name='zombie').count()

    return JsonResponse({
        'success': 1,
        'message': 'position is set',
        'data': {
            'count_kills': count_kills,
            'count_lives': team.standard_of_living,
            'count_flamethrower': team.count_flamethrower,
            'count_jacket': team.count_jacket
        }
    })


def create_prod_base(request):
    create_zombies()
    create_things(JACKET, 'http://img.ipev.ru/2018/11/21/imgpsh_fullsize-1.png')
    create_things(FLAMETHROWER, 'http://img.ipev.ru/2018/11/21/imgpsh_fullsize.png')

    return JsonResponse({
        'success': 1,
        'message': 'Ok'
    })


def create_things(things, url):
    for tiem in Team.objects.all():
        rand = random.sample(things, 8)
        for ind in range(0, len(rand)):
            Marker(name='{}-{}'.format(rand[ind][0], tiem.name), latitude=float(rand[ind][2]), longitude=float(rand[ind][3]),
                   type=MarkerType.objects.filter(name=rand[ind][1]).first(), url_image=url,
                   priority=ind, casualty_radius=-1, key=rand[ind][4], team=tiem).save()


def create_zombies():
    for z in ZOMBIES:
        Marker(name=z[0], latitude=float(z[2]), longitude=float(z[3]),
               type=MarkerType.objects.filter(name=z[1]).first(),
               url_image='http://img.ipev.ru/2018/11/21/imgpsh_fullsize-2.png',
               priority=-1, casualty_radius=20, key='Null').save()


ZOMBIES = [
    ['Z-1', 'zombie', '54.33282', '48.38576'],
    ['Z-2', 'zombie', '54.33304', '48.38303'],
    ['Z-3', 'zombie', '54.33325', '48.38648'],
    ['Z-4', 'zombie', '54.33354', '48.38601'],
    ['Z-5', 'zombie', '54.33375', '48.38387'],
    ['Z-6', 'zombie', '54.33389', '48.38429'],
    ['Z-7', 'zombie', '54.33504', '48.38449'],
    ['Z-8', 'zombie', '54.33528', '48.38414'],
    ['Z-9', 'zombie', '54.33245', '48.38695'],
    ['Z-10', 'zombie', '54.33312', '48.38644'],
    ['Z-11', 'zombie', '54.33196', '48.3849'],
    ['Z-12', 'zombie', '54.33191', '48.3871'],
    ['Z-13', 'zombie', '54.33197', '48.38788'],
    ['Z-14', 'zombie', '54.33267', '48.38725'],
    ['Z-15', 'zombie', '54.33257', '48.38539']
]

FLAMETHROWER = [
    ['F-1', 'flamethrower', '54.33361', '48.38572', '0e9ZbTo3Xr7diqzQOdIdiuYq2'],
    ['F-2', 'flamethrower', '54.3337', '48.38389', 'G2h4dqNKHR0JELAsmUkueih8m'],
    ['F-3', 'flamethrower', '54.33374', '48.38444', 'hMt0HStBjypSdUmX8zfkoK7ii'],
    ['F-4', 'flamethrower', '54.33266', '48.3884', 'WovKuRDdncnrhiaourXu9Xysl'],
    ['F-5', 'flamethrower', '54.33348', '48.38697', 'Z9HsqcWxRRhBzowtQ2TZBaJkP'],
    ['F-6', 'flamethrower', '54.33212', '48.38782', 'VclwEyzk4EIlG9KmHHgye6gik'],
    ['F-7', 'flamethrower', '54.33159', '48.38516', 'd5732vbTS4P0M8QROFWb2oaF1'],
    ['F-8', 'flamethrower', '54.33271', '48.38452', 'QiRvDbow0KBOcvz0AvoWQV8Mv'],
    ['F-9', 'flamethrower', '54.33392', '48.38633', 'rOyrt1C0Zyeo3Z4S36uPmMQHp'],
    ['F-10', 'flamethrower', '54.3314', '48.38682', 'ACsW8J1En2Ke7CWpFYxmvTI2j']
]

JACKET = [
    ['J-1', 'jacket', '54.33464', '48.38364', 'JsHKPlGAYRyBkfQuRiSaDmsbB'],
    ['J-2', 'jacket', '54.33248', '48.3862', 'ruxNE1Z63qAAjCs4X98n0YNas'],
    ['J-3', 'jacket', '54.33258', '48.38734', 'F3ojIbHJD73MRFHY5uGTxJ2R5'],
    ['J-4', 'jacket', '54.33189', '48.38657', 'hV4bhXDXrgGiv44hnrxBfOr8j'],
    ['J-5', 'jacket', '54.33474', '48.38467', 'gdA9pRyFpojYc7nH449o8HOfW'],
    ['J-6', 'jacket', '54.33301', '48.3842', 'yLFfe2o4HCakRpoRBGUOFxnpE'],
    ['J-7', 'jacket', '54.3342', '48.38556', 'qhPT9Od4tVSrGiKOkbFoOorm4'],
    ['J-8', 'jacket', '54.33278', '48.38809', 'CUmbdCYjV5JlWBrv8gWK432WM'],
    ['J-9', 'jacket', '54.3329', '48.38601', 'sm1Ay8h0R7u7pRNSqtwxgTfrt'],
    ['J-10', 'jacket', '54.33365', '48.38645', 'pKwQBMieRYC2YQmnQLEPBhejm']
]
