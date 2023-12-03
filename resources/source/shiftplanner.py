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
SERVICE_ACCOUNT_FILE = os.path.join(KEYS_DIR, 'ultimate-shift-planning-a1f509220989.json')

# Function to read CSV file and return data as a list of lists
def read_csv(file_path):
    print("Attempting to read from:", file_path)
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return list(reader)

# Function to connect to Google Calendar API
def google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

# Function to check employee availability
def is_employee_available(service, employee, shift_start, shift_end):
    # Convert shift times to RFC3339 timestamp
    shift_start_rfc3339 = shift_start.isoformat() + 'Z'
    shift_end_rfc3339 = shift_end.isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=employee['cal-id'],
        timeMin=shift_start_rfc3339,
        timeMax=shift_end_rfc3339,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    for event in events:
        if 'summary' in event and event['summary'].lower() == employee['name'].lower():
            return True  # Preferred shift
        elif 'summary' not in event:
            return True  # Available
        elif "block" in event.get('summary', '').lower():
            return False  # Blocked

    return False  # No events means not available

# Function to assign shifts
def assign_shifts(shifts, employees, service):
    total_shifts = sum(len(shifts[file]) - 1 for file in SHIFT_FILES)  # Exclude header row
    assigned_shifts = 0

    for shift_file in SHIFT_FILES:
        for shift in shifts[shift_file][1:]:  # Skip header row
            shift_date = datetime.strptime(shift[0], "%Y-%m-%d")
            shift_start = shift_date + timedelta(hours=int(shift[2].split(":")[0]), minutes=int(shift[2].split(":")[1]))
            shift_end = shift_date + timedelta(hours=int(shift[3].split(":")[0]), minutes=int(shift[3].split(":")[1]))
            shift_duration = float(shift[4])

            for employee in employees[1:]:  # Skip header row
                if (employee[2] == '1' and shift_file == "laser_shifts.csv") or (employee[3] == '1' and shift_file == "holo_shifts.csv"):
                    if is_employee_available(service, employee, shift_start, shift_end):
                        # Assign shift
                        shift[-1] = employee[0]  # Assign employee name to shift
                        employee[5] = str(float(employee[5]) + shift_duration)  # Update work_hours
                        employee[6] = str(float(employee[6]) - shift_duration)  # Update remaining_hours
                        assigned_shifts += 1
                        print(f"Currently processing {assigned_shifts}/{total_shifts} shifts. Please wait.")
                        break

            if shift[-1] == "":  # Check if shift is still unassigned
                shift[-1] = "OFFEN"

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

    # Initialize emp_output with additional columns, skipping the header row
    emp_output = [employees[0] + ['work_hours', 'remaining_hours']]  # Include header with new columns
    for emp in employees[1:]:  # Start from the second row to skip the header
        try:
            max_hours = float(emp[4])
        except ValueError:
            print(f"Error converting max_hours to float for employee: {emp}")
            continue
        emp_output.append(emp + [0, max_hours])  # Add work_hours (0) and remaining_hours (equal to max_hours)

    # Connect to Google Calendar
    service = google_calendar_service()

    # Assign shifts
    assign_shifts(shifts, employees, service)

    # Write updated data back to CSV files
    for shift_file in SHIFT_FILES:
        month_name = calendar.month_name[int(shifts[shift_file][1][0].split('-')[1])].lower()
        output_file = os.path.join(TMP_DIR, f"{shift_file.split('_')[0]}_{month_name}.csv")
        write_csv(output_file, shifts[shift_file])

    # Prepare and write employee output
    write_csv(os.path.join(TMP_DIR, "emp_output.csv"), emp_output)

if __name__ == "__main__":
    main()
