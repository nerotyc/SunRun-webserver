from django.apps import AppConfig


class GroupConfig(AppConfig):
    name = 'group'

    # def ready(self):
        # from group.score_updater import read_strava_data
        # read_strava_data()
        # from group.update_service import start
        # start()
