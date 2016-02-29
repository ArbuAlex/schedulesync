#-*- coding: utf-8 -*-
import httplib2
import os
import pprint

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import time
import json
import urllib2

import argparse
    
parser = argparse.ArgumentParser(parents=[tools.argparser])
parser.add_argument('-w', '--weeks', type=int, help='How many weeks should be syncronized after current (defalult: 0).', default=0)
parser.add_argument('-c', '--calendar', help='Google Calendar ID.', nargs=1, required=True) # Calendar ID
parser.add_argument('-p', '--person', help='Person ID from JS of gu-unpk.ru.', nargs=1, required=True) # Person ID
parser.add_argument('-s', '--secret', help='Google client secret file (default: client_secret.json in current directory).', default=['client_secret.json']) # File should be generated by Google Apps
flags = parser.parse_args()

SCOPES_RO = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = flags.secret[0] 
PERSON_ID = flags.person[0] # Reverse-engineered JS-query http://gu-unpk.ru/schedule
CALENDAR_ID = flags.calendar[0] 
QUERY = 'http://gu-unpk.ru/schedule//%s///%s/printschedule' # Reverse-engineered JS-query http://gu-unpk.ru/schedule

APPLICATION_NAME = 'ScheduleSync'
TZ = '+03:00'

TIMETABLE = { 
    # Workday
    False: [['08:15', '09:45'], ['09:55', '11:25'], ['12:00', '13:30'], ['13:40', '15:10'], ['15:20','16:50'], ['17:00', '18:30'], ['18:40', '20:10'], ['20:15', '21:45']], 
    # Saturday
    True: [['08:15', '09:45'], ['09:55', '11:25'], ['11:35', '13:05'], ['13:15', '14:45'], ['14:55', '16:25'], ['16:35', '18:05']] 
}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('.')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

def previous_monday_timestamp(date=datetime.date.today()):
    """Calculate previous Monday timestamp.

        Returns:
            Timestamp of previous Monday.
    """
    today = date
    current_monday = today - datetime.timedelta(days=today.weekday()) 
    current_monday_timestamp = 1000 * int(time.mktime(current_monday.timetuple()))
    return current_monday_timestamp

def is_saturday(day):
    return day == 6

def week_events(service, date=datetime.date.today()):
    """Get already added list of events.

        Returns:
            List of events.
    """
    eventsResult = service.events().list(
        calendarId=CALENDAR_ID, 
        timeMin=(date - datetime.timedelta(days=date.weekday())).isoformat() + 'T00:00:00' + TZ, # from Monday
        timeMax=(date + datetime.timedelta(days=6-date.weekday())).isoformat() + 'T00:00:00' + TZ, # till Sunday
        singleEvents=True,
        orderBy='startTime').execute() 
    events = eventsResult.get('items', [])
    return events

def remove_same_events(service, events, the_event):
    """Remove all (added by this script!) same (key is event start time) events.
    """
    for e in events:
        if 'description' in e.keys() and e['description'] == APPLICATION_NAME:
            if the_event['start']['dateTime'] == e['start']['dateTime']: 
                # Remove obsolete event from calendar
                service.events().delete(calendarId=CALENDAR_ID, eventId=e['id']).execute() 
        # Remove obsolete event from list
        events = [e for e in events 
            if the_event['start']['dateTime'] != e['start']['dateTime'] and 
                'description' in e.keys() and 
                e['description'] == APPLICATION_NAME] 

def events_from_schedule(schedule, current_monday):
    """Make events list in prepared for google calendar api format.

        Returns: List of prepared events
    """
    result = []
    for s in schedule:
        event_name = ' '.join([s['TitleSubject'], '(' + s['TypeLesson'] + ')', s['Korpus'] + '-' +s['NumberRoom'], s['title']])
        time_shift = time.strptime(TIMETABLE[ is_saturday(s['DayWeek']) ][ s['NumberLesson']-1 ][0], '%H:%M')
        lesson_start = datetime.datetime.fromtimestamp(current_monday/1000)
        lesson_start += datetime.timedelta(days=s['DayWeek']-1, hours=time_shift.tm_hour, minutes=time_shift.tm_min)
        lesson_end = lesson_start + datetime.timedelta(hours=1, minutes=30) # Duration of lesson is one hour and thirty minutes.
        cur_event = {
          'summary': event_name,
          'start': {
            'dateTime': lesson_start.isoformat(sep='T') + TZ
          },
          'end': {
            'dateTime': lesson_end.isoformat(sep='T') + TZ
          },
          'reminders': {
            'useDefault': True,
          },
          'description': APPLICATION_NAME # For identifying events added by this program
        }
        result.append(cur_event)
    return result


def main():
    """Fill calendar by university timetable

    Creates events in special user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    for w in xrange(0, flags.weeks + 1):
        current_monday = previous_monday_timestamp(datetime.date.today() + datetime.timedelta(weeks=w))

        try:
            schedule = json.load(urllib2.urlopen( QUERY % (PERSON_ID, str(current_monday))) )
        except urllib2.URLError:
            schedule = None

        old_events = week_events(service, datetime.date.today() + datetime.timedelta(weeks=w))

        if not schedule:
            print 'No upcoming events found.'
        else:
            schedule = events_from_schedule(schedule, current_monday)
            for cur_event in schedule:
                remove_same_events(service, old_events, cur_event)
                cur_event = service.events().insert(calendarId=CALENDAR_ID, body=cur_event).execute()
                print 'Event created: %s' % (cur_event.get('htmlLink'))
            # Remove_cancelled_events(service, old_events, schedule)
            for e in old_events:
                if 'description' in e.keys() and e['description'] == APPLICATION_NAME:
                    if [s for s in schedule if s['start']['dateTime'] == e['start']['dateTime']] == []: 
                        print "The event was cancelled: "
                        pprint.pprint(e)
                        service.events().delete(calendarId=CALENDAR_ID, eventId=e['id']).execute()                                       


if __name__ == '__main__':
    main()
