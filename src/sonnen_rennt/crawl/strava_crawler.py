from datetime import datetime, timedelta

import re

import numpy
import pytz
import yaml
import time

import os
import os
import sys
import inspect

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sonnen_rennt.settings')
import django

django.setup()

from run.models import Run, StravaRun
from group import score_updater

strava_email = None
strava_password = None


def read_credential():
    global strava_email, strava_password

    if str(os.getcwd()).split("\\")[-1] == 'crawl':
        file_path = '../'
    else:  # currently in sonnen_rennt folder
        file_path = ''

    file_path = file_path + '../../.config/.crawl-strava_login.yml'

    with open(file_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if data:
            strava_email = data['strava_email']
            strava_password = data['strava_password']
            print('credentials read!')
        else:
            print('reading credentials failed!')


def write_credential(email, password):

    if str(os.getcwd()).split("\\")[-1] == 'crawl':
        file_path = '../'
    else:  # currently in sonnen_rennt folder
        file_path = ''

    file_path = file_path + '../../.config/.crawl-strava_login.yml'

    with open(file_path, 'w+') as f:
        credentials = {
            'strava_email': email,
            'strava_password': password,
        }
        data = yaml.dump(credentials, f)


"""
returns list with runs dicts: 
[
    {...},
    {...}, 
    ...
]
"""


def _get_distance_elevation_duration_from_inline_stats_block(inline_stats_block):
    distance = 0  # km
    elevation_gain = 0  # m
    duration = timedelta(seconds=0)

    stats_children = inline_stats_block.find_elements_by_tag_name('li')
    for li_child in stats_children:
        if li_child.get_attribute('title') == "Distance":
            distance_str = li_child.text
            distance = float(str(distance_str).replace("km", ""))
        elif li_child.get_attribute('title') == "Elev Gain":
            elevation_gain_str = str(li_child.text)
            if "km" in elevation_gain_str:
                elevation_gain = float(elevation_gain_str.replace("km", "")) * 1000
            else:
                elevation_gain = float(elevation_gain_str.replace("m", ""))

        elif li_child.get_attribute('title') == "Time":
            duration_str = str(li_child.text)

            hours_str = re.search('[0-9]+h', duration_str)
            mins_str = re.search('[0-9]+m', duration_str)
            secs_str = re.search('[0-9]+s', duration_str)

            hours = hours_str[0].replace("h", "") if hours_str else 0
            mins = mins_str[0].replace("m", "") if mins_str else 0
            secs = secs_str[0].replace("s", "") if secs_str else 0

            duration = timedelta(hours=int(hours), minutes=int(mins), seconds=int(secs))

    return {
        'distance': distance,
        'elevation_gain': elevation_gain,
        'duration': duration,
    }


def _get_name_title_profile_handle_type_distance_elevation_duration(feed_entry: WebElement):
    name = None
    title = None
    profile_handle = None
    type = Run.TYPE_RUN
    distance = 0  # km
    elevation_gain = 0  # m
    duration = timedelta(seconds=0)

    name_field = feed_entry.find_element_by_class_name("entry-athlete")
    if name_field:
        name = name_field.text
        try:
            profile_handle_str = str(name_field.get_attribute("href") or "0").replace(
                "https://www.strava.com/athletes/", ""
            )
            profile_handle = numpy.uint64(profile_handle_str)
        except:
            x = True

    title_field = feed_entry.find_element_by_class_name("entry-title")
    if title_field:
        title = title_field.text
        title = title_field.text

    inline_stats_block = feed_entry.find_element_by_class_name("inline-stats")
    if inline_stats_block:
        data = _get_distance_elevation_duration_from_inline_stats_block(inline_stats_block)
        distance = data['distance']
        elevation_gain = data['elevation_gain']
        duration = data['duration']

    return {
        'name': name,
        'title': title,
        'profile_handle': profile_handle,
        'type': type,
        'distance': distance,
        'elevation_gain': elevation_gain,
        'duration': duration,
    }


def _get_time_start(feed_entry):
    time_start = None
    timestamp_field = feed_entry.find_element_by_class_name("timestamp")
    if timestamp_field:
        time_start_str = timestamp_field.get_attribute("datetime")
        # "%Y-%m-%d %H:%M:%S" ||  # 2021-04-24 10:03:26 UTC
        time_start_raw = datetime.strptime(str(time_start_str).replace("UTC", "+00:00"), '%Y-%m-%d %H:%M:%S %z')
        time_start_raw.replace(tzinfo=pytz.utc)
        time_start = time_start_raw.astimezone(tz=pytz.timezone("Europe/Berlin"))

        # TODO improve this procedure:
        time_start_berlin_str = str(time_start).split("+")[0]
        time_start = datetime.strptime(time_start_berlin_str, '%Y-%m-%d %H:%M:%S')

    return time_start


def fetch_all_strava_runs():
    read_credential()

    # TODO auto enable at production
    # chrome_options = Options()
    # chrome_options.add_argument("start-maximized")  # open Browser in maximized mode
    # chrome_options.add_argument("disable-infobars")  # disabling infobars
    # chrome_options.add_argument("--disable-extensions")  # disabling extensions
    # chrome_options.add_argument("--disable-gpu")  # applicable to windows os only
    # chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    # driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)

    driver = webdriver.Chrome()
    # driver.get("http://www.python.org")
    # driver.get("https://www.strava.com/clubs/849711/recent_activity")  # old club
    driver.get("https://www.strava.com/clubs/895672/recent_activity")
    print(driver.title)

    # assert "Sonnen" in driver.title

    if "Log In" in driver.title:
        print('login needed...')
        send_button = driver.find_element_by_id('login-button')

        if not strava_email or not strava_password:
            print("error: email or password emapty!")
            exit(0)

        email_field = driver.find_element_by_id('email')
        password_field = driver.find_element_by_id('password')
        remember_me_checkbox = driver.find_element_by_id('remember_me')

        if not email_field or not password_field:
            print("error: email/password input field(s)!")
            exit(0)

        email_field.send_keys(strava_email)
        password_field.send_keys(strava_password)
        if remember_me_checkbox:
            remember_me_checkbox.send_keys(Keys.SPACE)

        print("waiting for 2 seconds...")
        time.sleep(2)

        print("submitting...")
        password_field.submit()

        print("waiting for 5 seconds...")
        time.sleep(5)

    # ----------------------------------------
    # scrolling down

    print("start scrolling...")
    elem = driver.find_element_by_tag_name("body")
    no_of_pagedowns = 50

    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.4)
        no_of_pagedowns -= 1

    print("scrolling done.")
    # ----------------------------------------

    run_list = []

    print("analyzing feed...")
    feed = driver.find_element_by_class_name("feed-moby")

    # [solo activities]++++++++++++++++++
    feed_entries = feed.find_elements_by_class_name("activity")  # only solo runs

    for feed_entry in feed_entries:
        if not "group-activity" in feed_entry.get_attribute("class"):
            activity_handle = None
            route_link = None
            time_start = _get_time_start(feed_entry)

            activity_handle = 0
            try:
                activity_handle_str = str(feed_entry.get_attribute('id') or "0").replace("Activity-", "")
                activity_handle = numpy.uint64(activity_handle_str)
            except:
                print("activity_handle could not be parsed!")

            try:
                route_img_element = feed_entry.find_element_by_class_name("entry-image")
                if route_img_element:
                    route_handle_str = str(route_img_element.get_attribute('href') or "0").replace(
                        "https://www.strava.com/activities/", ""
                    )
                    route_handle = numpy.uint64(route_handle_str)
            except:
                x = True

            data = _get_name_title_profile_handle_type_distance_elevation_duration(feed_entry)
            name = data['name']
            title = data['title']
            profile_handle = data['profile_handle']
            type = data['type']
            distance = data['distance']
            elevation_gain = data['elevation_gain']
            duration = data['duration']

            if activity_handle > 0 and name and title and time_start and (distance > 0) and duration:
                run_list.append({
                    'activity_handle': activity_handle,
                    'name': name,
                    'time_start': time_start,
                    'profile_handle': profile_handle,
                    'route_handle': route_handle,
                    'title': title,
                    'type': type,
                    'distance': distance,
                    'elevation_gain': elevation_gain,
                    'duration': duration,
                })
            else:
                print("One field was empty, so inserting StravaRun is not possible! Ignoring this run...")

    # [group activities]++++++++++++++++++
    feed_entries = driver.find_elements_by_class_name("group-activity")

    for feed_entry in feed_entries:
        activity_handle = None
        route_handle = 0
        time_start = _get_time_start(feed_entry)

        entry_body = feed_entry.find_element_by_class_name("entry-body")
        if entry_body:
            try:
                route_link_element = entry_body.find_element_by_tag_name('a')
                if route_link_element:
                    route_handle_str = str(route_link_element.get_attribute('href') or "0").replace(
                        "https://www.strava.com/activities/", ""
                    )
                    route_handle = numpy.uint64(route_handle_str)
            except:
                x = True

        list_entries = feed_entry.find_element_by_class_name("list-entries")
        if list_entries:
            entry_detail_list = list_entries.find_elements_by_class_name("entity-details")
            for entry_detail in entry_detail_list:
                activity_handle = 0
                try:
                    activity_handle_str = str(entry_detail.get_attribute('id') or "0").replace("Activity-", "")
                    activity_handle = numpy.uint64(activity_handle_str)
                except:
                    print("activity_handle could not be parsed!")

                data = _get_name_title_profile_handle_type_distance_elevation_duration(entry_detail)
                name = data['name']
                title = data['title']
                profile_handle = data['profile_handle']
                type = data['type']
                distance = data['distance']
                elevation_gain = data['elevation_gain']
                duration = data['duration']

                if activity_handle > 0 and name and title and time_start and (distance > 0) and duration:
                    run_list.append({
                        'activity_handle': activity_handle,
                        'name': name,
                        'time_start': time_start,
                        'profile_handle': profile_handle,
                        'route_handle': route_handle,
                        'title': title,
                        'type': type,
                        'distance': distance,
                        'elevation_gain': elevation_gain,
                        'duration': duration,
                    })
                else:
                    print("One field was empty, so inserting StravaRun is not possible! Ignoring this run...")

    # ++++++++++++++++++

    driver.close()
    return run_list


def fetch_insert_strava_runs():
    all_query = StravaRun.objects

    for run in fetch_all_strava_runs():
        filtered = all_query.filter(strava_handle=run['activity_handle'])
        if filtered.exists():
            obj = StravaRun.objects.get(strava_handle=run['activity_handle'])

            if obj:
                obj.creator = run['name'],

                # obj.strava_handle = run['activity_handle'].real,
                # obj.profile_handle = run['profile_handle'].real,
                # obj.route_handle = run['route_handle'].real,

                obj.distance = run['distance'],
                obj.elevation_gain = run['elevation_gain'],

                obj.time_start = run['time_start'],
                obj.duration = run['duration'],
                obj.type = run['type'],
                obj.note = run['title'],

                try:
                    obj.save()
                except:
                    x = True

                print("Updated StravaRun:", run['name'], ":", run['title'])
            else:
                print("Error, object not found...")
        else:
            StravaRun(
                creator=run['name'],

                strava_handle=run['activity_handle'],
                profile_handle=run['profile_handle'],
                route_handle=run['route_handle'],

                distance=run['distance'],
                elevation_gain=run['elevation_gain'],

                time_start=run['time_start'],
                duration=run['duration'],
                type=run['type'],
                note=run['title'],
            ).save()
            print("Inserted StravaRun:", run['name'], ":", run['title'])

    print("Updating Strava stats...")
    score_updater.score_update_strava()
    print("Done.")


if __name__ == '__main__':
    fetch_insert_strava_runs()
