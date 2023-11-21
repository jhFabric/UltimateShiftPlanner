import os
import re
import csv
import calendar
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

## Directories & Network

# Set Base directory # Call Credentials JSON
ScriptPath = os.path.abspath(__file__)
HomeDir = os.path.dirname(os.path.dirname(os.path.dirname(ScriptPath)))

KeyFile = os.path.join(HomeDir, 'resources', 'keys',
                       'ultimate-shift-planning-ea113d5e1166.json')
Key = KeyFile

## Retrieve Data from Mitarbeiter Kalender in Google

# Calender
CALENDAR_NAME = 'mcisnbiilvaj5481i9cnloga40@group.calendar.google.com'
# CET timezone
cet = pytz.timezone('CET')
# convert UTC time to CET
def convert_utc_to_cet(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S%z')
    utc_time = utc_time.astimezone(pytz.utc)
    cet_time = utc_time.astimezone(cet)
    return cet_time.strftime('%Y-%m-%dT%H:%M:%S')
# Google Calender API
credentials = service_account.Credentials.from_service_account_file(
    Key, scopes=['https://www.googleapis.com/auth/calendar.readonly'])
service = build('calendar', 'v3', credentials=credentials)

## MAIN00 Create
# Variables
LaserShifts = []
# User Input
while True:
    month = input("Enter the month (e.g., '2023-11'): ")
    if re.match(r'\d{4}-\d{2}', month) and len(month) == 7:
        break
    print('Please repeat in the format jjjj-mm e.g. "2023-11"')

# Last day of the month
year, month_num = map(int, month.split('-'))
last_day = calendar.monthrange(year, month_num)[1]

# Start & end of month in UTC
start_of_month_utc = f'{month}-01T00:00:00Z'
end_of_month_utc = f'{month}-{last_day}T23:59:59Z'

# Retrieve events
events_result = service.events().list(
    calendarId=CALENDAR_NAME,
    timeMin=start_of_month_utc,
    timeMax=end_of_month_utc,
    singleEvents=True
).execute()

events = events_result.get('items', [])

# OutputPath
csv_output_file_path = os.path.join(HomeDir, 'tmp', 'laser_shifts.csv')

# Function to split date and time
def split_date_time(datetime_str):
    date, time = datetime_str.split('T')
    return date, time

# Function to get the name of the weekday
def get_weekday(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return weekdays[date_obj.weekday()]

# Function to calculate the duration between start and end times
def calculate_duration(start_time, end_time):
    start = datetime.strptime(start_time, '%H:%M:%S')
    end = datetime.strptime(end_time, '%H:%M:%S')
    duration = end - start
    # Convert duration to a formatted string like 'HH:MM'
    return f'{duration.seconds // 3600}h {duration.seconds % 3600 // 60}min'

# Filter and format
formatted_events = []
for event in events:
    if 'summary' in event and (event['summary'] == 'Halle 1' or event['summary'] == 'Halle 2'):
        start_date, start_time = split_date_time(convert_utc_to_cet(event['start']['dateTime']))
        end_date, end_time = split_date_time(convert_utc_to_cet(event['end']['dateTime']))

        event_info = {
            'day': start_date,
            'weekday': get_weekday(start_date),
            'start': start_time,
            'end': end_time,
            'time': calculate_duration(start_time, end_time),
            'shift': event['summary']
        }
        formatted_events.append(event_info)
        LaserShifts.append(event_info)

# Sort
sorted_events = sorted(formatted_events, key=lambda x: (x['day'], x['start']))

# Write to CSV
with open(csv_output_file_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['day', 'weekday', 'start', 'end', 'time', 'shift'])
    writer.writeheader()

    for event in sorted_events:
        writer.writerow(event)

print(f'Events retrieved and saved to {csv_output_file_path}')
## Hier weiter. Datenstruktur soll 
# print(LaserShifts)