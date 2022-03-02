import json
from datetime import datetime, timedelta, date

import re

import numpy
import pytz
import yaml
import time

import os
import sys
import inspect

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options

# [ LOGGING ] ############################################
import logging
logging.basicConfig(filename='strava_crawler.log', encoding='utf-8', level=logging.INFO)
##########################################################

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

sep = os.path.sep


def read_credential():
    global strava_email, strava_password

    if str(os.getcwd()).split(sep)[-1] == 'crawl':
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
    if str(os.getcwd()).split(sep)[-1] == 'crawl':
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

MONTHS_MAP = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


def _get_time_start(feed_entry):
    try:
        if feed_entry is None or len(str(feed_entry)) < 3:
            logging.warning("could not parse datetime: ", feed_entry)
            return None

        [datestr, timestr] = str(feed_entry).split(sep=' at ')
        if datestr is None or len(str(datestr)) < 3 \
                or timestr is None or len(str(timestr)) < 2:
            logging.warning("could not parse datetime: ", feed_entry)
            return None

        if "Today" in datestr:
            pdate = datetime.today()
        elif "Yesterday" in datestr:
            pdate = datetime.today() - timedelta(days=1)
        else:
            [daymonthstr, yearstr] = str(datestr).split(",")
            if daymonthstr is None or len(str(daymonthstr)) < 3 \
                    or yearstr is None or len(str(yearstr)) < 2:
                logging.warning("could not parse datetime: ", feed_entry)

            year = int(yearstr)
            [monthstr, daystr] = str(daymonthstr).split(' ')
            if monthstr is None or len(str(monthstr)) < 1 \
                    or daystr is None or len(str(daystr)) < 1:
                logging.warning("could not parse datetime: ", feed_entry)

            month = MONTHS_MAP[str(monthstr).strip()]
            day = int(daystr)
            pdate = date(year, month, day)



        ptime = datetime.strptime(timestr, "%I:%M %p").time()
        return pytz.timezone("Europe/Berlin").localize(datetime.combine(pdate, ptime, tzinfo=None))
    except Exception as ex:
        print("Parsing exception: ", feed_entry, "-", ex)
        logging.warning("Parsing exception: ", feed_entry, "-", ex)
        return None


def fetch_activity_detail(activity_id, driver):
    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f"https://www.strava.com/activities/{activity_id}")
        time.sleep(4.0)
        # ----------------------------------------
        # scrolling down

        distance = 0
        elevation_gain = 0
        moving_time = timedelta(seconds=0)

        print("start scrolling...")
        elem = driver.find_element(By.CLASS_NAME, "inline-stats")
        elements = str(elem.text).split('\n')
        # order not guaranteed:
        #   ['8.68km', 'Distance', '52:22', 'Moving Time', '6:02/km', 'Pace', '57', 'Relative Effort']
        if len(elements) % 2 != 0:
            logging.warning("failed to parse: " + str(elem.text).split('\n'))
            return None

        for i in range(0, int(len(elements) / 2)):
            tag = elements[2*i+1]
            val = elements[2*i]
            if tag == 'Distance':  # in km
                distance = float(re.sub(r"[,/a-zA-Z]+", "", str(val)))
            elif tag == 'Elevation':  # in m
                elevation_gain = float(re.sub(r"[,/a-zA-Z]+", '', str(val)))
            elif tag == 'Moving Time':  # in (hh:)mm:ss
                hms = str(val).split(':')
                if len(hms) == 3:
                    moving_time = timedelta(hours=float(hms[0]), minutes=float(hms[1]), seconds=float(hms[2]))

                elif len(hms) == 2:
                    moving_time = timedelta(minutes=float(hms[0]), seconds=float(hms[1]))

                else:
                    print("could not parse move time!", str(val))
                    logging.warning("could not parse move time! " + str(val))
                    return None


        elem = driver.find_element(By.CLASS_NAME, "more-stats")
        elements = str(elem.text).split('\n')
        # order not guaranteed: ['Elevation', '208m', 'Calories', '754', 'Elapsed Time', '53:03']
        if len(elements) % 2 != 0:
            logging.warning("failed to parse: " + str(elem.text).split('\n'))
            return None

        for i in range(0, int(len(elements) / 2)):
            """reversed compared to first list!!"""
            tag = elements[2 * i]
            val = elements[2 * i + 1]
            if tag == 'Distance':  # in km
                    distance = float(re.sub(r"[,/a-zA-Z]+", "", str(val)))
            elif tag == 'Elevation':  # in m
                    elevation_gain = float(re.sub(r"[,/a-zA-Z]+", '', str(val)))
            elif tag == 'Moving Time':  # in (hh:)mm:ss
                hms = str(val).split(':')
                if len(hms) == 3:
                    moving_time = timedelta(hours=int(hms[0]), minutes=int(hms[1]), seconds=int(hms[2]))

                elif len(hms) == 2:
                    moving_time = timedelta(minutes=int(hms[0]), seconds=int(hms[1]))

                else:
                    print("could not parse move time!", str(val))
                    logging.warning("could not parse move time! " + str(val))
                    return None
        # ----------------------------------------
        time.sleep(1.0)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'w')
    except Exception as ex:
        print("fetch detail failed:", ex)
        logging.warning(f"fetch detail failed:{ex}")

    return distance, elevation_gain, moving_time


def fetch_all_strava_runs(club_id: int):
    read_credential()

    if sys.platform == "linux" or sys.platform == "linux2":
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")  # open Browser in maximized mode
        chrome_options.add_argument("disable-infobars")  # disabling infobars
        chrome_options.add_argument("--disable-extensions")  # disabling extensions
        chrome_options.add_argument("--disable-gpu")  # applicable to windows os only
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    else:  # platform == "win32"
        driver = webdriver.Chrome()

    driver.get(f"https://www.strava.com/clubs/{club_id}/recent_activity")  # old club: 849711
    print(driver.title)

    # assert "Sonnen" in driver.title

    if "Log In" in driver.title:
        print('login needed...')
        send_button = driver.find_element(By.ID, 'login-button')

        if not strava_email or not strava_password:
            print("error: email or password empty!")
            exit(0)

        email_field = driver.find_element(By.ID, 'email')
        password_field = driver.find_element(By.ID, 'password')
        remember_me_checkbox = driver.find_element(By.ID, 'remember_me')

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
    elem = driver.find_element(By.TAG_NAME, "body")
    no_of_pagedowns = 50

    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.4)
        no_of_pagedowns -= 1

    print("scrolling done.")
    # ----------------------------------------

    run_list = []

    print("analyzing feed...")
    feed = driver.find_element(By.CLASS_NAME, "feed")

    feed_entries = feed.find_elements(By.CLASS_NAME, "react-feed-component")  # only solo runs

    for feed_entry in feed_entries:
        try:
            react_data = feed_entry.get_attribute('data-react-props')
            json_data = json.loads(react_data)

            # Activity / GroupActivity
            react_activity_type = feed_entry.get_attribute('data-react-class')
            react_data_type = json_data['entity']

            # [solo activities]++++++++++++++++++
            if react_activity_type == "Activity" or react_data_type == 'Activity':
                json_activity = json_data['activity']
                if json_activity is None:
                    logging.error("activity parse failure: json.activity null; json: ", json_data)
                    continue

                athlete_data = json_activity['athlete']
                if athlete_data is None:
                    logging.warning("athlete_data was null during parsing: jsonData: " + string(json_data))
                    continue

                athlete_id = int(athlete_data['athleteId'])
                athlete_name = athlete_data['athleteName']

                activity_id = int(json_activity['id'])
                activity_name = json_activity['activityName']

                timeAndLocation = json_activity['timeAndLocation'] or {}
                if timeAndLocation is None:
                    logging.warning("timeAndLocation was null during parsing: jsonData: " + string(json_data))
                    continue
                displayDateAtTime = timeAndLocation['displayDateAtTime']
                displayDate = timeAndLocation['displayDate']

                move_type = json_activity['type']
                # Run, Ride
                if move_type == 'Run':
                    move_type = Run.TYPE_RUN
                elif move_type == 'Ride':
                    move_type = Run.TYPE_BIKE
                else:
                    logging.warning("Couldn't identify move type: ", move_type)
                    print("Couldn't identify move type: ", move_type)
                    continue

                route_link = None
                if (json_activity['mapAndPhotos'] is not None
                        and json_activity['mapAndPhotos']['activityMap'] is not None):
                    route_link = json_activity['mapAndPhotos']['activityMap']['url']

                time_start = _get_time_start(displayDateAtTime)

                name = athlete_name
                title = activity_name
                profile_handle = athlete_id
                type = move_type

                (distance, elevation_gain, duration) = fetch_activity_detail(activity_id, driver)

                if activity_id > 0 and name and title and time_start and (distance > 0) and duration:
                    run_list.append({
                        'activity_handle': activity_id,
                        'name': name,
                        'time_start': time_start,
                        'profile_handle': profile_handle,
                        'route_link': route_link,
                        'title': title,
                        'type': type,
                        'distance': distance,
                        'elevation_gain': elevation_gain,
                        'duration': duration,
                    })
                else:
                    print("One field was empty, so inserting StravaRun is not possible! Ignoring this run...")

            # [group activities]++++++++++++++++++
            elif react_activity_type == "GroupActivity" or react_data_type == 'GroupActivity':
                json_raw_data = json_data['rowData']

                if json_raw_data is None:
                    continue

                for json_activity in json_raw_data['activities']:
                    athlete_id = int(json_activity['athlete_id'])
                    athlete_name = json_activity['athlete_name']

                    activity_id = int(json_activity['activity_id'])
                    activity_name = json_activity['name']

                    start_datetime = json_activity['start_date']
                    if start_datetime is None:
                        print("start_date was none: ", json_activity)
                        logging.warning("start_date was none: ", json_activity)
                        continue
                    time_start = pytz.utc.localize(datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%SZ'))

                    move_type = json_activity['type']
                    # Run, Ride
                    if move_type == 'Run':
                        move_type = Run.TYPE_RUN
                    elif move_type == 'Ride':
                        move_type = Run.TYPE_BIKE
                    else:
                        logging.warning("Couldn't identify move type: ", move_type)
                        print("Couldn't identify move type: ", move_type)
                        continue

                    route_link = None
                    if json_activity['activity_map'] is not None:
                        route_link = json_activity['activity_map']['url']

                    name = athlete_name
                    title = activity_name
                    profile_handle = athlete_id
                    type = move_type

                    (distance, elevation_gain, duration) = fetch_activity_detail(activity_id, driver)

                    if activity_id > 0 and name and title and time_start and (distance > 0) and duration:
                        run_list.append({
                            'activity_handle': activity_id,
                            'name': name,
                            'time_start': time_start,
                            'profile_handle': profile_handle,
                            'route_link': route_link,
                            'title': title,
                            'type': type,
                            'distance': distance,
                            'elevation_gain': elevation_gain,
                            'duration': duration,
                        })
                    else:
                        print("One field was empty, so inserting StravaRun is not possible! Ignoring this run...")

            # ++++++++++++++++++
            else:
                print(f'Unimplemented activity type: [{react_activity_type}] -> data: {react_data}')
                logging.error(f'Unimplemented activity type: [{react_activity_type}] -> data: {react_data}')
        except Exception as ex:
            print("parse error: " + str(ex))
            logging.warning("parse error: " + str(ex))

    driver.close()
    return run_list


def read_club_list():
    with open('../../../.config/.crawl-clublist', 'r') as clublistfile:
        return list(map(lambda x: int(str(x).strip()), clublistfile.readlines()))


def fetch_insert_strava_runs():
    all_query = StravaRun.objects

    for club_id in read_club_list():
        for run in fetch_all_strava_runs(club_id):
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

                    strava_group_handle=club_id,
                    strava_handle=run['activity_handle'],
                    profile_handle=run['profile_handle'],
                    route_link=run['route_link'],

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
