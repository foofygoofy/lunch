import argparse
import copy
import datetime
import httplib2
import json
import math
import os
import random
import re
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/469639486059/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'config/client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

with open('./config/members.json') as infile:
    MEMBERS = json.loads(infile.read())

with open('./config/settings.json') as infile:
    SETTINGS = json.loads(infile.read())

def create_event(events, attendees, date):
    date_str = date.strftime('%Y-%m-%d')
    event = {
        'summary': SETTINGS['summary'],
        'description': SETTINGS['description'],
        'attendees': [ { 'email': attendee['email'] } for attendee in attendees ],
        'start': {
            'dateTime': '%sT%s' % (date_str, SETTINGS['startTime']),
            'timeZone': SETTINGS['timeZone'],
        },
        'end': {
            'dateTime': '%sT%s' % (date_str, SETTINGS['endTime']),
            'timeZone': SETTINGS['timeZone'],
        },
    }
    try:
        request = events.insert(
            calendarId=SETTINGS['calendar']['id'],
            sendNotifications=SETTINGS['sendNotifications'],
            body=event,
        )
        request.execute()

    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run the application to re-authorize")


def main(argv):
    # Parser for command-line arguments.
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage('match.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)
    events = service.events()

    lunchEventStartDate = datetime.datetime.today().date() + datetime.timedelta(
        days=SETTINGS['runDaysBefore'])
    lunchEventEndDate = lunchEventStartDate + datetime.timedelta(
        days=SETTINGS['periodDays']-1)
    eventDate = lunchEventStartDate

    # Start matching
    match_queue = copy.copy(MEMBERS)
    pair = []

    while len(match_queue) > 0:
        i = int(math.floor(random.random() * len(match_queue)))
        picked = match_queue[i]
        pair.append(picked)
        match_queue.remove(picked)
        if len(pair) == 2:
            print "%s %s" % (pair[0]['name'], pair[1]['name'])
            create_event(events, pair, eventDate)
            if eventDate == lunchEventEndDate:
                eventDate = lunchEventStartDate
            else:
                eventDate = eventDate + datetime.timedelta(days=1)
            pair = []

    if pair:
        match_queue = copy.copy(MEMBERS)
        match_queue.remove(pair[0])
        i = int(math.floor(random.random() * len(match_queue)))
        pair.append(match_queue[i])
        print "%s %s" % (pair[0]['name'], pair[1]['name'])
        create_event(events, pair, eventDate)

if  __name__ == "__main__":
    main(sys.argv)
