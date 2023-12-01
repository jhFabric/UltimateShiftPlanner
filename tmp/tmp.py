import os
import re
import csv
import calendar
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

## Configuration

# Calendar IDs
CALENDAR_LASER_ID = 'mcisnbiilvaj5481i9cnloga40@group.calendar.google.com'
CALENDAR_HOLO_ID = 'o1l0or1r8bhuhjf6jr8t784tnc@group.calendar.google.com'

# Other constants
CET = pytz.timezone('CET')
KEY_FILE = os.path.join(HomeDir, 'resources', 'keys', 'ultimate-shift-planning-ea113d5e1166.json')

# Google Calendar API
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=['https://www.googleapis.com/auth/calendar.readonly'])
service = build('calendar', 'v3', credentials=credentials)

# Function to process calendar
def process_calendar(calendar_id, event_names, csv_filename):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_of_month_utc,
        timeMax=end_of_month_utc,
        singleEvents=True
    ).execute()

    events = events_result.get('items', [])
    formatted_events = []

    for event in events:
        if 'summary' in event and event['summary'] in event_names:
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

    # Sort and write to CSV
    sorted_events = sorted(formatted_events, key=lambda x: (x['day'], x['start']))
    csv_output_file_path = os.path.join(HomeDir, 'tmp', csv_filename)
    
    with open(csv_output_file_path, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['day', 'weekday', 'start', 'end', 'time', 'shift'])
        writer.writeheader()
        for event in sorted_events:
            writer.writerow(event)

    print(f'Events from {calendar_id} retrieved and saved to {csv_output_file_path}')

# User Input for Month
# ... [Your existing code for user input] ...

# Process each calendar
process_calendar(CALENDAR_LASER_ID, ['Halle 1', 'Halle 2'], 'laser_shifts.csv')
process_calendar(CALENDAR_HOLO_ID, ['Café 1', 'Café 2'], 'holo_shifts.csv')
