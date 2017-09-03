from datetime import datetime
from dateutil import parser


class Event(object):

    def __init__(self, event_object):
        self._event_object = event_object
        self._title = event_object.get('summary')
        self._start = event_object.get('start')
        self._end = event_object.get('end')
        self._location = event_object.get('location')

    def get_event_object(self):
        return self._event_object

    def get_title(self):
        return self._title

    def get_start_datetime(self):
        start_string = self._start.get("dateTime", self._start.get('date'))
        return parser.parse(start_string).replace(tzinfo=None)