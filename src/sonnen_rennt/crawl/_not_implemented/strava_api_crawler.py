import json
import time
from symbol import continue_stmt

import requests
import configparser

from datetime import timedelta, datetime

import schedule
from django.db import connection
from jsonify.convert import jsonify
from oauthlib.oauth2 import BackendApplicationClient

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sonnen_rennt.settings')
import django

django.setup()

from run.models import Run, StravaRun


def _write_config(access_token, refresh_token):
    config = configparser.ConfigParser()
    config.set(config.default_section, option='access_token', value=access_token)
    config.set(config.default_section, option='refresh_token', value=refresh_token)
    with open('.strava_access.ini', 'w') as configfile:
        config.write(configfile)
    print('Updated .strava_access.ini with new data!')


def _read_config_access_token():
    config = configparser.ConfigParser()
    config.read('.strava_access.ini')
    return config.get(config.default_section, 'access_token')


def _read_config_refresh_token():
    config = configparser.ConfigParser()
    config.read('.strava_access.ini')
    return config.get(config.default_section, 'refresh_token')


# API ACCESS #######################

def fetch_first_access_token():
    # global client_id TODO load from .strava_access.ini
    # global client_secret TODO load from .strava_access.ini

    # step 1: Browser
    # authorize_url = 'https://www.strava.com/oauth/authorize?client_id=64034&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,profile:read_all,activity:read'
    # redirects to url with ?code=AUTH_CODE
    authorization_code = 'a1a69f266dfbc70aedc17ccf11083faf97e7fa75'

    # step 2: get access token with the auth_code
    token_url = 'http://www.strava.com/oauth/token'
    token_request_type = 'POST'

    myobj = {
        # 'client_id': client_id,
        # 'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
    }

    access_token_response = requests.post(token_url, data=myobj)

    if access_token_response.status_code == 200:
        print('successfully retrieved access token for the first time!')
        dict_response = json.loads(access_token_response.text)
        access_token = dict_response['access_token']
        refresh_token = dict_response['refresh_token']
        print('access_token:', access_token)
        print('refresh_token:', refresh_token)
        _write_config(access_token, refresh_token)

    else:
        print('failed! ERROR', access_token_response.status_code)
        print(access_token_response.text)


def refresh_access_token():
    # global client_id TODO load from .strava_access.ini
    # global client_secret TODO load from .strava_access.ini

    # step 2: get access token with the auth_code
    token_url = 'http://www.strava.com/oauth/token'
    token_request_type = 'POST'

    refresh_token = _read_config_refresh_token()

    myobj = {
        # 'client_id': client_id,
        # 'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    access_token_response = requests.post(token_url, data=myobj)

    if access_token_response.status_code == 200:
        print('successfully refreshed access token!')
        dict_response = json.loads(access_token_response.text)
        access_token = dict_response['access_token']
        refresh_token = dict_response['refresh_token']
        print('access_token:', access_token)
        print('refresh_token:', refresh_token)
        _write_config(access_token, refresh_token)

    else:
        print('failed! ERROR', access_token_response.status_code)
        _write_config('', '')
        print(access_token_response.text)


# TODO pagination
def fetch_insert_group_activities(access_token):
    group_id = 849711
    page = 1
    per_page = 100

    print("use access_token:", access_token)

    continue_fetch = True

    while continue_fetch:
        # List Club Activities
        request_url = 'https://www.strava.com/api/v3/clubs/' + str(group_id) + '/activities'
        params = {
            'page': page,
            'per_page': per_page,
        }
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json'
        }
        api_response = requests.get(request_url, headers=headers, params=params)
        print(api_response.text)

        if api_response and api_response.status_code == 200:
            dict_response = json.loads(api_response.text)

            _db_delete_strava_runs()

            try:
                dict_size = len(dict_response)

                for run in dict_response:
                    # run_type_raw = str(run['type']).lower()
                    run_type = "RUN"
                    # if (run_type_raw == "run"
                    #     or run_type_raw == "hike"
                    #     or run_type_raw == "walk"
                    #     or run_type_raw == ""
                    # ):
                    #     print()
                    #
                    # elif (run_type_raw == "ride"
                    #         or run_type_raw == "e-bike ride"
                    #         or run_type_raw == "inline skate"
                    # ):
                    #     print()
                    #
                    # elif (run_type_raw == "ride"
                    #         or run_type_raw == "inline skate"
                    # ):
                    #     print()

                    run_distance = float(run['distance']) / 1000.0
                    run_elevation_gain = float(run['total_elevation_gain'])
                    duration_seconds = run['moving_time']
                    duration = timedelta(minutes=int(duration_seconds / 60), seconds=duration_seconds % 60)
                    run_name = str(run['name']).encode("ascii", errors="ignore").decode()
                    print("run_name:", run_name)
                    raw_athlete = run['athlete']
                    athlete = raw_athlete['firstname'] + " " + raw_athlete['lastname']

                    StravaRun(
                        # TODO strava_handle=
                        # TODO: strava_group_handle
                        creator=athlete,
                        distance=run_distance,
                        elevation_gain=run_elevation_gain,
                        duration=duration,
                        type=run_type,
                        note=run_name
                    ).save()

                if dict_size < per_page:
                    continue_fetch = False
                else:
                    page += 1

            except:
                continue_fetch = False

        else:
            print('failed! ERROR', api_response.status_code)
            continue_fetch = False
            print(api_response.text)


####################################


def _db_delete_strava_runs():
    StravaRun.objects.all().delete()


####################################


def schedule_strava_sync():
    print("Starting Strava sync...")

    # get new access token
    refresh_access_token()

    # check if access and refresh token are present
    access_token = _read_config_access_token()
    refresh_token = _read_config_refresh_token()

    if len(access_token) > 0 and len(refresh_token) > 0:
        fetch_insert_group_activities(access_token)
    else:
        print("something went wrong with the auth keys!")

    print("Synced Strava data....")


ever_n = 12
call_counter = 0


def schedule_call():
    return
    # global ever_n TODO load from .strava_access.ini
    # global call_counter TODO load from .strava_access.ini

    # if call_counter > 0:
    #     print("Noch", call_counter, " Stunden bis zum Strava Sync!")
    #     call_counter -= 1
    # else:
    #     schedule_strava_sync()
    #     call_counter = ever_n


if __name__ == '__main__':
    schedule_strava_sync()
    schedule.every(1).hours.do(schedule_call)

    while 1:
        schedule.run_pending()
        time.sleep(1)
