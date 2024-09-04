import os
import sys
import calendar
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def google_calendar_service():
    key_path = resource_path(os.path.join(
        '..', 'keys', 'ultimate-shift-planning-a1f509220989.json'))
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=['https://www.googleapis.com/auth/calendar.readonly'])
    service = build('calendar', 'v3', credentials=credentials)
    return service


def format_event_date(date_str, all_day=False):
    if all_day:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%d.%m.%Y')
    else:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%d.%m.%Y %H:%M')


def get_calendar_events(service, calendar_id, start_of_month, end_of_month):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_of_month,
        timeMax=end_of_month,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = []
    for event in events_result.get('items', []):
        if 'dateTime' in event['start']:
            start_date = format_event_date(event['start']['dateTime'])
            end_date = format_event_date(event['end']['dateTime'])
            all_day = False
        elif 'date' in event['start']:
            start_date = format_event_date(event['start']['date'], all_day=True)
            end_date = format_event_date(event['end']['date'], all_day=True)
            all_day = True
        else:
            continue

        events.append({
            'start_date': start_date,
            'end_date': end_date,
            'title': event.get('summary', 'No Title'),
            'all_day': all_day
        })
    return events


def save_events_to_file(output_path, month_input, events):
    file_path = os.path.join(output_path, f"urlaub_events_{month_input}.txt")
    with open(file_path, 'w') as file:
        for event in events:
            if event['all_day']:
                file.write(f"{event['title']}\t{event['start_date']} - {event['end_date']} (All Day)\n")
            else:
                file.write(f"{event['title']}\t{event['start_date']} - {event['end_date']}\n")


def main():
    service = google_calendar_service()

    month_input = input("Enter the month (e.g., '2023-11'): ")
    year, month = map(int, month_input.split('-'))
    start_of_month = f"{year}-{month:02d}-01T00:00:00Z"
    end_of_month = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}T23:59:59Z"

    urlaub_calendar_id = 'ss2jdk18vevkib95bhpmebacgc@group.calendar.google.com'

    events = get_calendar_events(service, urlaub_calendar_id, start_of_month, end_of_month)
    
    output_path = resource_path(os.path.join('..', '..', 'output', 'UrlaubTest'))
    os.makedirs(output_path, exist_ok=True)
    
    save_events_to_file(output_path, f"{year}-{month:02d}", events)

    print(f'Test successful. Events saved in {output_path}/urlaub_events_{month_input}.txt')


if __name__ == "__main__":
    main()
