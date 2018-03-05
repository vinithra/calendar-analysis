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

START_MONTH = 3
START_DATE = 12
END_MONTH = 3
END_DATE = 17
YEAR = 2018
FILENAME = '/Users/vinithra/code/gcal/cloudera_cal_metadata.csv'

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
  """Get the datetime version given a month and date in specified year
  Returns: datetime
  """
  return datetime.datetime(YEAR, month, date).isoformat() + 'Z'

def get_timestamp(time_unicode):
  """Gets the timestamp from a string representation
  """
  return parse(time_unicode)

def get_events(service):
  """Get the events using the Google calendar API and categorize them
  """
  # The start and end dates for the period we care about
  start_week = get_time(START_MONTH, START_DATE)
  end_week = get_time(END_MONTH, END_DATE) # non-inclusive

  # Get events from Google API
  # TODO: Currently only returning small number of events for testing purposes
  eventsResult = service.events().list(
    calendarId='primary', timeMin=start_week, timeMax=end_week, singleEvents=True,
    orderBy='startTime').execute()
  events = eventsResult.get('items', [])
  categorize_events(events)

def get_time_mins(event):
  """Get the string version of the time in minutes of an event
  """
  time = get_timestamp(event['end']['dateTime']) - get_timestamp(event['start']['dateTime'])
  time_mins = time.total_seconds() / 60
  time_mins_string = '{:.0f}'.format(time_mins)
  return time_mins_string

def categorize_events(events):
  """Get input on categories of events and write them to file
  """
  # catg_count = {}
  file_object = open(FILENAME, "a")

  # Parse the events and categorize the time taken
  if not events:
    print('No upcoming events found.')
  for event in events:
    time_mins = get_time_mins(event)

    categories = input(str(time_mins) + ' mins: ' + event['summary'] + ': ')
    write_data(file_object, event, time_mins, categories)

  file_object.close()

def write_data(file_object, event, time_mins, categories):
  """Write data to file according to schema:
  Event_name time_mins comma_delimited_categories
  except where category implies to be ignored
  """
  for category in categories.split(','):
    if category == 'i':
      # Some events can be ignored
      return

  file_object.write(event['summary'] + '\t' +
                    event['end']['dateTime'] + '\t' +
                    event['start']['dateTime'] + '\t' +
                    time_mins + '\t' +
                    categories + '\n')

def print_categories(cateogries, time_mins):
  # Accept multiple categories
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
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  get_events(service)

if __name__ == '__main__':
  main()

# Pick up categories from past events. Can you figure out if they are recurring
# Process metadata
