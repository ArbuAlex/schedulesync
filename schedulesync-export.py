# -*- coding: utf-8 -*-
import os

from oauth2client import tools

import datetime
import time
import json
import urllib2

import argparse
from icalendar import Calendar, Event
from icalendar import vDatetime

parser = argparse.ArgumentParser(parents=[tools.argparser])
parser.add_argument('-id', help='ID from JS of oreluniver.ru.', nargs=1, required=True)  # Group or Person ID
parser.add_argument('-t', '--teacher', action='store_const', const=True, default=False)  # Shows that 'id' is Person ID
parser.add_argument('-w', '--weeks', type=int, help='How many weeks should be syncronized after current (defalult: 0).',
                    default=0)
parser.add_argument('-f', '--filename', type=str, help='ics-file for writing results', default='schedule.ics')
flags = parser.parse_args()

FILE_NAME = flags.filename
UID = flags.id[0]  # Could be retrieved from cookie http://oreluniver.ru/schedule
TEACHER = flags.teacher
QUERY_GROUP = 'http://oreluniver.ru/schedule//%s///%s/printschedule'  # JS-query for students http://oreluniver.ru/schedule
QUERY_TEACHER = 'http://oreluniver.ru/schedule/%s////%s/printschedule'  # JS-query for teachers http://oreluniver.ru/schedule

QUERY = QUERY_TEACHER if (TEACHER) else QUERY_GROUP
APPLICATION_NAME = 'ScheduleSync'
TZ = '+03:00'

cal = Calendar()
TIMETABLE = [['08:30', '10:00'], ['10:10', '11:40'], ['12:00', '13:30'], ['13:40', '15:10'], ['15:20', '16:50'],
             ['17:00', '18:30'], ['18:40', '20:10'], ['20:15', '21:45']]


def previous_monday_timestamp(date=datetime.date.today()):
    """Calculate previous Monday timestamp.

        Returns:
            Timestamp of previous Monday.
    """
    today = date
    current_monday = today - datetime.timedelta(days=today.weekday())
    current_monday_timestamp = 1000 * int(time.mktime(current_monday.timetuple()))
    return current_monday_timestamp


def events_from_schedule(schedule, current_monday):
    """Make events list in prepared for google calendar api format.

        Returns: List of prepared events.
    """
    result = []
    for s in schedule:
        event_name = ' '.join(
            [s['TitleSubject'], '(' + s['TypeLesson'] + ')'])
        if TEACHER:
            event_name = event_name + ' ' + s['title']
        time_shift = time.strptime(TIMETABLE[s['NumberLesson'] - 1][0], '%H:%M')
        lesson_start = datetime.datetime.fromtimestamp(current_monday / 1000)
        lesson_start += datetime.timedelta(days=s['DayWeek'] - 1, hours=time_shift.tm_hour, minutes=time_shift.tm_min)
        lesson_end = lesson_start + datetime.timedelta(hours=1,
                                                       minutes=30)  # Duration of lesson is one hour and thirty minutes.
        lesson_location = s['Korpus'] + '-' + s['NumberRoom']
        cur_event = {
            'summary': event_name,
            'location': lesson_location,
            'start': {
                'dateTime': lesson_start
            },
            'end': {
                'dateTime': lesson_end
            },
            'reminders': {
                'useDefault': True,
            },
            'description': APPLICATION_NAME  # For identifying events added by this program
        }
        result.append(cur_event)
    return result


def main():
    """Fill calendar by university timetable

    Creates events in schedule.ics
    """
    # Init calendar info
    cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
    cal.add('version', '2.0')
    cal.add('METHOD', 'PUBLISH')
    cal.add('CALSCALE', 'GREGORIAN')
    cal.add('X-WR-NAME', 'Schedule')
    cal.add('X-WR-TIMEZONE', 'Europe/Moscow')

    for w in xrange(0, flags.weeks + 1):
        current_monday = previous_monday_timestamp(datetime.date.today() + datetime.timedelta(weeks=w))

        try:
            schedule = json.load(urllib2.urlopen(QUERY % (UID, str(current_monday))))

        except urllib2.URLError:
            schedule = None

        if not schedule:
            print 'No upcoming events found.'
        else:
            schedule = events_from_schedule(schedule, current_monday)
            for lesson in schedule:
                event = Event()
                event.add('dtstart', vDatetime(lesson['start']['dateTime']))
                event.add('dtend', vDatetime(lesson['end']['dateTime']))
                event.add('summary', lesson['summary'])
                event.add('location', lesson['location'])
                event.add('description', lesson['description'])
                print 'Event created: %s' % (event['summary'])
                cal.add_component(event)

    # \\f = open(os.path.join(FILE_NAME), 'w')
    with open(FILE_NAME,mode='w',buffering = -1) as f:
        f.write(cal.to_ical())
        f.close()


if __name__ == '__main__':
    main()
