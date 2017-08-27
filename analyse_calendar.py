
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from datetime import date
from dateutil.parser import parse

"""Interactively categorize calendar events to determine time spent
per category"""

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = '/Users/vinithra/.credentials/client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


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

def get_time(month, date):
  """Get the datetime version given a month and date in 2017
  Returns: datetime
  """
  return datetime.datetime(2017, month, date).isoformat() + 'Z'

def get_timestamp(time_unicode):
  """Gets the timestamp from a string representation"""
  return parse(time_unicode)

def get_events(service):
  # The start and end dates for the period we care about
  start_week = get_time(8, 21)
  end_week = get_time(8, 26) # non-inclusive

  # Get events from Google API
  eventsResult = service.events().list(
    calendarId='primary', timeMin=start_week, timeMax=end_week, singleEvents=True,
    orderBy='startTime', maxResults=3).execute()
  events = eventsResult.get('items', [])

  catg_count = {}

  # Parse the events and categorize the time taken
  if not events:
    print('No upcoming events found.')
  for event in events:
    time = get_timestamp(event['end']['dateTime']) - get_timestamp(event['start']['dateTime'])
    time_mins = time.total_seconds() / 60
    
    categories = input(str(time_mins) + ' mins: ' + event['summary'] + ': ')
    for category in categories.split(','):
      if category == 'i':
          # Some events can be ignored
          continue
      elif category in catg_count:
          catg_count[category] = catg_count[category] + time_mins
      else:
          catg_count[category] = time_mins

  print(catg_count)

def main():
  """Shows basic usage of the Google Calendar API.

  Creates a Google Calendar API service object and outputs a list of the next
  10 events on the user's calendar.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  get_events(service)

if __name__ == '__main__':
  main()

# Check into github
# Create persistence by week, so as to see variance over time
# Create clues to automatically categorize
