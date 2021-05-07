
import os
import yaml


def setup_strava_login():

    strava_email = input("Please enter your Strava account's email: ")
    strava_password = input("Please enter your Strava account's password: ")

    file_path = '../.config/crawl-strava_login.yml'

    with open(file_path, 'w+') as f:
        credentials = {
            'strava_email': strava_email,
            'strava_password': strava_password,
        }
        data = yaml.dump(credentials, f)


if __name__ == '__main__':
    setup_strava_login()