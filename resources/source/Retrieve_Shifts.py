import os
import csv
import calendar
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Set Base directory # Call Credentials JSON
ScriptPath = os.path.abspath(__file__)
HomeDir = os.path.dirname(os.path.dirname(os.path.dirname(ScriptPath)))

KeyFile = os.path.join(HomeDir, 'resources', 'keys',
                       'ultimate-shift-planning-ea113d5e1166.json')
Key = KeyFile

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

# Main
# User Input
month = input("Enter the month (e.g., '2023-11'): ")
year, month_num = map(int, month.split('-'))

# Last day of the month
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

# Write 2 CSV
with open(csv_output_file_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['start', 'end'])
    writer.writeheader()

    for event in events:
        if 'summary' in event and (event['summary'] == 'Halle 1' or event['summary'] == 'Halle 2'):
            event_info = {
                'start': convert_utc_to_cet(event['start']['dateTime']),
                'end': convert_utc_to_cet(event['end']['dateTime'])
            }
            writer.writerow(event_info)

print(f'Events retrieved and saved to {csv_output_file_path}')