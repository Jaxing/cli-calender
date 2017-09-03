from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

from event import Event

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


class Calender(object):

    def __init__(self, service):
        super(Calender, self).__init__()
        self.service = service

    @staticmethod
    def get_credentials():
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_upcoming_events(self, number_of_events, calender_ids):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events = []

        for calender_id in calender_ids:
            calender_events = self._get_upcoming_events(number_of_events, calender_id)

            if not len(calender_events) == 0:
                events.append(calender_events)

        events = reduce(Calender.merge_event_lists, events)

        return events[:number_of_events]

    def _get_upcoming_events(self, number_of_events, calender_id):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId=calender_id, timeMin=now, maxResults=number_of_events, singleEvents=True,
            orderBy='startTime').execute()
        events = map(Event, events_result.get('items', []))
        return events

    def get_calendar_ids(self, show_all=False):
        calendar_ids = []

        for calender in self.service.calendarList().list().execute()['items']:
            if calender.get('selected') or show_all:
                calendar_ids.append(calender['id'])

        return calendar_ids

    @staticmethod
    def merge_event_lists(event_list_a, event_list_b):
        """Assumes that the event list are individually sorted.
        Implements merge part of quicksort to merge the to lists.
        Merges them in ascending order"""

        merged_list = []

        index_active = index_inactive = 0

        active_list = event_list_a
        inactive_list = event_list_b

        while not len(active_list) == index_active:
            if Calender._compare_events(active_list[index_active], inactive_list[index_inactive]) > 0:
                merged_list.append(active_list[index_active])
                index_active += 1
            else:
                merged_list.append(inactive_list[index_inactive])
                index_inactive += 1

                tmp_list = active_list
                active_list = inactive_list
                inactive_list = tmp_list

                tmp_index = index_active
                index_active = index_inactive
                index_inactive = tmp_index

        if index_inactive < len(inactive_list):
            for i in range(index_inactive, len(inactive_list)):
                merged_list.append(inactive_list[i])

        return merged_list

    @classmethod
    def _compare_events(cls, event1, event2):
        start1 = event1.get_start_datetime()
        start2 = event2.get_start_datetime()

        return 1 if start1 < start2 else -1

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = Calender.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calender = Calender(service)

    ids = calender.get_calendar_ids()
    events = calender.get_upcoming_events(10, ids)

    if not events:
        print('No upcoming events found.')
    for event in events:
        print(event.get_start_datetime(), event.get_title())




if __name__ == '__main__':
    main()
