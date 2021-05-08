
import os
import yaml
from pathlib import Path

from dotenv import load_dotenv

DOT_ENV_STRING = str(str(Path(__file__).resolve().parent.parent.parent.parent) + "\.config\.django.env")
load_dotenv(DOT_ENV_STRING)


def setup_strava_login():
    print("----------------------------------")

    strava_email = input("Please enter your Strava account's email: ")
    strava_password = input("Please enter your Strava account's password: ")

    file_path = '../.config/.crawl-strava_login.yml'

    with open(file_path, 'w+') as f:
        credentials = {
            'strava_email': strava_email,
            'strava_password': strava_password,
        }
        data = yaml.dump(credentials, f)


def setup_django():
    print("----------------------------------")
    print("Setting up django:")

    secret_key = input("Django Secret Key: ")
    debug = input("Debug (True/False): ")
    db_host = input("Database Host: ")
    db_name = input("Database Name: ")
    db_user = input("Database User: ")
    db_password = input("Database User Password: ")
    email_host = input("Email Host: ")
    email_port = input("Email Port: ")
    email_tls = input("Email TLS (True/False): ")
    email_host_user = input("Email Host User: ")
    email_host_password = input("Email Host Password: ")
    email_server_email = input("Server Email: ")

    file_string = \
f"""SECRET_KEY='{secret_key}'
DEBUG={debug}
DATABASE_HOST='{db_host}'
DATABASE_NAME='{db_name}'
DATABASE_USER='{db_user}'
DATABASE_PASSWORD='{db_password}'
EMAIL_HOST ='{email_host}'
EMAIL_PORT = '{email_port}'
EMAIL_USE_TLS = {email_tls}
EMAIL_HOST_USER = '{email_host_user}'
EMAIL_HOST_PASSWORD = '{email_host_password}'
SERVER_EMAIL = '{email_server_email}'\n
"""

    file_path = '../.config/.django.env'

    text_file = open(file_path, "w")
    text_file.write(file_string)
    text_file.close()

    print("----------------------------------")

if __name__ == '__main__':
    setup_strava_login()
    setup_django()