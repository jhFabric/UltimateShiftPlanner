import os
import csv
import sys
import calendar
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def read_employee_names(csv_file_path):
    employee_names = []
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            employee_names.append(row[0])
    return employee_names


def google_calendar_service():
    key_path = resource_path(os.path.join(
        '..', 'keys', 'ultimate-shift-planning-a1f509220989.json'))
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=['https://www.googleapis.com/auth/calendar.readonly'])
    service = build('calendar', 'v3', credentials=credentials)
    return service


def format_event_date(date_str):
    dt = datetime.fromisoformat(date_str)
    return dt.strftime('%d.%m.%Y;%H:%M')


def get_calendar_events(service, calendar_id, start_of_month, end_of_month):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_of_month,
        timeMax=end_of_month,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return [
        {
            'start_date': format_event_date(event['start']['dateTime']).split(';')[0],
            'start_time': format_event_date(event['start']['dateTime']).split(';')[1],
            'end_time': format_event_date(event['end']['dateTime']).split(';')[1],
            'title': event.get('summary', 'No Title'),
            'calendar_id': calendar_id
        }
        for event in events_result.get('items', []) if 'dateTime' in event['start']
    ]


def initialize_employee_events(employee_names):
    return {name: [["" for _ in range(12)] for _ in range(31)] for name in employee_names}


def assign_events_to_employees(employee_names, events):
    employee_data = {name: [["" for _ in range(12)] for _ in range(31)] for name in employee_names}

    for event in events:
        title = event['title'].lower()
        start_date = event['start_date']
        start_time = event['start_time']
        end_time = event['end_time']
        calendar_id = event['calendar_id']
        
        # Find employee name from the title if it's in the list
        employee_name = next((name for name in employee_names if name.lower() in title), None)
        
        if employee_name:
            day = int(start_date.split('.')[0]) - 1  # Convert day to 0-based index
            if calendar_id == 'mcisnbiilvaj5481i9cnloga40@group.calendar.google.com':
                if 'krank' not in title and 'pause' not in title:
                    employee_data[employee_name][day][0] = start_time
                    employee_data[employee_name][day][1] = end_time
                elif 'krank' in title:
                    employee_data[employee_name][day][4] = start_time
                    employee_data[employee_name][day][5] = end_time
                elif 'pause' in title:
                    employee_data[employee_name][day][8] = start_time
                    employee_data[employee_name][day][9] = end_time
            elif calendar_id == 'o1l0or1r8bhuhjf6jr8t784tnc@group.calendar.google.com':
                if 'krank' not in title and 'pause' not in title:
                    employee_data[employee_name][day][2] = start_time
                    employee_data[employee_name][day][3] = end_time
                elif 'krank' in title:
                    employee_data[employee_name][day][6] = start_time
                    employee_data[employee_name][day][7] = end_time
                elif 'pause' in title:
                    employee_data[employee_name][day][10] = start_time
                    employee_data[employee_name][day][11] = end_time

    return employee_data


def save_employee_events(output_path, month_input, employee_events):
    month_dir = os.path.join(output_path, month_input)
    os.makedirs(month_dir, exist_ok=True)
    for name, days in employee_events.items():
        file_path = os.path.join(month_dir, f"{name}_{month_input}.txt")
        with open(file_path, 'w') as file:
            for day in days:
                file.write('\t'.join(day) + '\n')


def main():
    employees_file = resource_path(os.path.join('..', 'data', 'employees.csv'))
    employee_names = read_employee_names(employees_file)

    service = google_calendar_service()

    month_input = input("Enter the month (e.g., '2023-11'): ")
    year, month = map(int, month_input.split('-'))
    start_of_month = f"{year}-{month:02d}-01T00:00:00Z"
    end_of_month = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}T23:59:59Z"

    calendar_ids = [
        'mcisnbiilvaj5481i9cnloga40@group.calendar.google.com',
        'o1l0or1r8bhuhjf6jr8t784tnc@group.calendar.google.com'
    ]

    all_events = []
    for cal_id in calendar_ids:
        events = get_calendar_events(service, cal_id, start_of_month, end_of_month)
        all_events.extend(events)

    employee_events = assign_events_to_employees(employee_names, all_events)
    output_path = resource_path(os.path.join('..', '..', 'output', 'Stundenauswertung'))
    save_employee_events(output_path, f"{year}-{month:02d}", employee_events)

    print('Auswertung erfolgreich. Dateien unter /output/.')


if __name__ == "__main__":
    main()
