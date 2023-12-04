import os
import csv
import pytz
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil import parser

# Constants and configurations
ScriptPath = os.path.abspath(__file__)
HOME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(ScriptPath)))
RESOURCES_DIR = os.path.join(HOME_DIR, "resources")
KEYS_DIR = os.path.join(RESOURCES_DIR, "keys")
DATA_DIR = os.path.join(RESOURCES_DIR, "data")
TMP_DIR = os.path.join(HOME_DIR, "tmp")
SHIFT_FILES = ["laser_shifts.csv", "holo_shifts.csv"]
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.csv")
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = os.path.join(
    KEYS_DIR, 'ultimate-shift-planning-a1f509220989.json')

# Function to read CSV file and return data as a list of lists


def read_csv(file_path):
    print("Attempting to read from:", file_path)
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        data = list(reader)
#        print(f"Data read from {file_path}:", data)  # Debug print
        return data

# Function to connect to Google Calendar API
def google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def fetch_and_write_employee_events(service, employees):
    # Define the date range for February 2024
    start_date = datetime(2024, 2, 1, 0, 0, 0)  # Start of February
    end_date = datetime(2024, 3, 1, 0, 0, 0)  # Start of March (end of February)

    for employee in employees[1:]:  # Skip header
        print(f"Current employee data: {employee}")  # Debug print
        calendar_id = employee[1].strip()
        employee_name = employee[0].strip()
        output_file_path = os.path.join(TMP_DIR, f"{employee_name}_events.csv")

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['day', 'weekday', 'start', 'end', 'time', 'shift'])  # Header

            for event in events:
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                end_str = event['end'].get('dateTime', event['end'].get('date'))
                start_dt = datetime.fromisoformat(start_str)
                end_dt = datetime.fromisoformat(end_str)

                day = start_dt.strftime('%Y-%m-%d')
                weekday = start_dt.strftime('%A')
                start_time = start_dt.strftime('%H:%M:%S')
                end_time = end_dt.strftime('%H:%M:%S')
                duration = (end_dt - start_dt).total_seconds() / 3600  # Duration in hours
                event_name = event.get('summary', 'No Title')

                writer.writerow([day, weekday, start_time, end_time, duration, event_name])


# Function to check employee availability
def is_employee_available(service, employee, shift_start, shift_end):
    # Ensure shift_start and shift_end are offset-aware
    if shift_start.tzinfo is None or shift_start.tzinfo.utcoffset(shift_start) is None:
        shift_start = parser.parse(shift_start.isoformat() + 'Z')
    if shift_end.tzinfo is None or shift_end.tzinfo.utcoffset(shift_end) is None:
        shift_end = parser.parse(shift_end.isoformat() + 'Z')

    try:
        events_result = service.events().list(
            calendarId=employee[1],  # Assuming employee['cal-id'] is at index 1
            timeMin=shift_start.isoformat(),
            timeMax=shift_end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except Exception as e:
        print(f"Error fetching calendar events for {employee[0]}: {e}")
        return False

    events = events_result.get('items', [])

    for event in events:
        event_start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_end_str = event['end'].get('dateTime', event['end'].get('date'))
        event_start = datetime.fromisoformat(event_start_str).replace(tzinfo=pytz.utc)  # Ensure offset-aware with UTC
        event_end = datetime.fromisoformat(event_end_str).replace(tzinfo=pytz.utc)  # Ensure offset-aware with UTC

        # Check if event is blocking
        if "block" in event.get('summary', '').lower():
            if event_start < shift_end and event_end > shift_start:
                print(f"Blocked by event: {event['summary']} for {employee[0]}")
                return False

    # If no blocking event is found, employee is available
    return True


# Function to assign shifts
def assign_shifts(shifts, employees, service):
    total_shifts = sum(len(shifts[file]) - 1 for file in SHIFT_FILES)
    assigned_shifts = 0

    for shift_file in SHIFT_FILES:
        for shift in shifts[shift_file][1:]:  # Skip header row
            shift_date_str, _, shift_start_str, shift_end_str, _ = shift[:5]
            shift_date = datetime.strptime(shift_date_str, "%Y-%m-%d")
            shift_start = shift_date + timedelta(hours=int(shift_start_str.split(":")[0]), minutes=int(shift_start_str.split(":")[1]))
            shift_end = shift_date + timedelta(hours=int(shift_end_str.split(":")[0]), minutes=int(shift_end_str.split(":")[1]))
            shift_duration = float(shift[4])

            print(f"Processing shift: Date: {shift_date_str}, Start: {shift_start_str}, End: {shift_end_str}")

            shift_assigned = False
            for employee in employees[1:]:  # Skip header row
                # Debug print to check the structure of each employee
                print(f"Employee data in assign_shifts: {employee}")

                if (employee[2] == '1' and shift_file == "laser_shifts.csv") or (employee[3] == '1' and shift_file == "holo_shifts.csv"):
                    print(f"Checking employee: {employee[0]} for shift {shift_start_str} to {shift_end_str}")
                    if is_employee_available(service, employee, shift_start, shift_end):
                        shift[-1] = employee[0]

                        # Additional check for the length of the employee list
                        if len(employee) >= 8:
                            print(f"Before update - Work hours: {employee[6]} (Type: {type(employee[6])}), Remaining hours: {employee[7]} (Type: {type(employee[7])})")
                            employee[6] = str(float(employee[6]) + shift_duration)  # Update work_hours
                            employee[7] = str(float(employee[7]) - shift_duration)  # Update remaining_hours
                        else:
                            print(f"Error: Employee list does not have the expected number of elements. Employee data: {employee}")

                        assigned_shifts += 1
                        print(f"Assigned {shift} to {employee[0]}")
                        shift_assigned = True
                        break

            if not shift_assigned:
                print(f"No suitable employee found for shift: Date: {shift_date_str}, Start: {shift_start_str}, End: {shift_end_str}")
                shift[-1] = "OFFEN"

    print(f"Total shifts processed: {assigned_shifts}/{total_shifts}")

# Function to write data to CSV
def write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Main Program


def main():

    # Read shifts and employee data
    shifts = {file: read_csv(os.path.join(TMP_DIR, file)) for file in SHIFT_FILES}
    employees = read_csv(EMPLOYEES_FILE)
    print("Employees loaded:", employees)  # Debug print

    # Initialize emp_output with additional columns, skipping the header row
    # Include header with new columns
    emp_output = [employees[0] + ['work_hours', 'remaining_hours']]
    for emp in employees[1:]:  # Start from the second row to skip the header
        try:
            max_hours = float(emp[4])
        except ValueError:
            print(f"Error converting max_hours to float for employee: {emp}")
            continue
        # Add work_hours (0) and remaining_hours (equal to max_hours)
        emp_output.append(emp + [0, max_hours])

    # Connect to Google Calendar
    service = google_calendar_service()

    # Fetch and write employee events
    fetch_and_write_employee_events(service, employees)

    for emp in emp_output[1:]:  # Debug print to check structure
        print(f"Employee in emp_output before assign_shifts: {emp}")

    # Assign shifts
    assign_shifts(shifts, emp_output, service)

    # Write updated data back to CSV files
    for shift_file in SHIFT_FILES:
        month_name = calendar.month_name[int(
            shifts[shift_file][1][0].split('-')[1])].lower()
        output_file = os.path.join(
            TMP_DIR, f"{shift_file.split('_')[0]}_{month_name}.csv")
        write_csv(output_file, shifts[shift_file])

    # Prepare and write employee output
    write_csv(os.path.join(TMP_DIR, "emp_output.csv"), emp_output)


if __name__ == "__main__":
    main()
