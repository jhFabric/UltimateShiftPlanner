import os
import csv
import pytz
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

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
        print(f"Data read from {file_path}:", data)  # Debug print
        return data

# Function to connect to Google Calendar API


def google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

# Function to check employee availability


def is_employee_available(service, employee, shift_start, shift_end):
    # Debug print to confirm function is called
    print(f"Checking availability for employee: {employee[0]}")

    # Convert shift times to RFC3339 timestamp
    shift_start_rfc3339 = shift_start.isoformat() + 'Z'
    shift_end_rfc3339 = shift_end.isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId=employee[1],  # Assuming employee['cal-id'] is at index 1
            timeMin=shift_start_rfc3339,
            timeMax=shift_end_rfc3339,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except Exception as e:
        print(f"Error fetching calendar events for {employee[0]}: {e}")
        return False

    events = events_result.get('items', [])
    print(f"Events found for {employee[0]}: {len(events)}")  # Debug print

    events = events_result.get('items', [])

    print(f"Checking availability for employee: {employee[0]} for shift {shift_start} to {shift_end}")
    for event in events:
        event_start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_end_str = event['end'].get('dateTime', event['end'].get('date'))
        event_start = datetime.fromisoformat(event_start_str)
        event_end = datetime.fromisoformat(event_end_str)

        print(f"Checking event: {event.get('summary', 'No Title')}, Start: {event_start}, End: {event_end}")

        # Check if event is blocking
        if "block" in event.get('summary', '').lower():
            print(f"Blocked by event: {event['summary']} for {employee[0]}")
            return False

        # Check if the event spans the entire shift duration or partially overlaps
        if event_start <= shift_start and event_end >= shift_end:
            if event['summary'].lower() == employee[0].lower():
                print(f"Preferred shift found: {event['summary']} for {employee[0]}")
                return True
            print(f"Available for shift: {shift_start} to {shift_end}, found event: {event['summary']} for {employee[0]}")
            return True

    print(f"No suitable event found for shift: {shift_start} to {shift_end} for {employee[0]}")
    return False  # No suitable events found

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
                if (employee[2] == '1' and shift_file == "laser_shifts.csv") or (employee[3] == '1' and shift_file == "holo_shifts.csv"):
                    print(f"Checking employee: {employee[0]} for shift {shift_start_str} to {shift_end_str}")
                    if is_employee_available(service, employee, shift_start, shift_end):
                        shift[-1] = employee[0]
                        employee[5] = str(float(employee[5]) + shift_duration)
                        employee[6] = str(float(employee[6]) - shift_duration)
                        assigned_shifts += 1
                        print(f"Assigned {shift} to {employee[0]}")
                        shift_assigned = True
                        break

            if not shift_assigned:
                print(f"No suitable employee found for shift: Date: {shift_date_str}, Start: {shift_start_str}, End: {shift_end_str}")
                shift[-1] = "OFFEN"

    print(f"Total shifts processed: {assigned_shifts}/{total_shifts}")

# Function to write data back to CSV


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

    # Assign shifts
    assign_shifts(shifts, employees, service)

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
