import os
import csv
import pytz
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil import parser
from collections import deque

# Constants and configurations
ScriptPath = os.path.abspath(__file__)
HOME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(ScriptPath)))
RESOURCES_DIR = os.path.join(HOME_DIR, "resources")
KEYS_DIR = os.path.join(RESOURCES_DIR, "keys")
DATA_DIR = os.path.join(RESOURCES_DIR, "data")
TMP_DIR = os.path.join(HOME_DIR, "tmp")
OUTPUT_DIR = os.path.join(HOME_DIR, "output")
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
        return data

# Function to connect to Google Calendar API
def google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

# Function to fetch and write employee events
def fetch_and_write_employee_events(service, employees, month, year):
    # Calculate the start and end dates for the given month
    start_date = datetime(year, month, 1, 0, 0, 0)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        end_date = datetime(year, month + 1, 1, 0, 0, 0)

    for employee in employees[1:]:  # Skip header
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
            writer.writerow(['day', 'weekday', 'start', 'end', 'time', 'shift'])

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

def prepare_employee_data(employees):
    emp_open = [['Name', 'work_hours', 'remaining_hours']]
    for emp in employees[1:]:
        print("Debug - Employee data:", emp)  # Debug print

        try:
            remaining_hours = float(emp[4])  # Convert to float as it will be used for calculations
        except ValueError:
            print("Error converting remaining hours to float for:", emp)  # Error print
            continue  # Skip if conversion fails
        except IndexError:
            print("Error: Not enough data in row for:", emp)  # Error print for missing data
            continue  # Skip if row is short

        emp_open.append([emp[0], 0.00, remaining_hours])  # Initialize work_hours with 0.00
    return emp_open


# Function to check employee availability
def is_employee_available(service, employee, shift_start, shift_end):
    if shift_start.tzinfo is None or shift_start.tzinfo.utcoffset(shift_start) is None:
        shift_start = parser.parse(shift_start.isoformat() + 'Z')
    if shift_end.tzinfo is None or shift_end.tzinfo.utcoffset(shift_end) is None:
        shift_end = parser.parse(shift_end.isoformat() + 'Z')

    try:
        events_result = service.events().list(
            calendarId=employee[1],
            timeMin=shift_start.isoformat(),
            timeMax=shift_end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except Exception as e:
        print(f"Error fetching calendar events for {employee[0]}: {e}")
        return False

    events = events_result.get('items', [])

    # If there are no events in the calendar for the shift period, return False (not available)
    if not events:
        return False

    for event in events:
        event_start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_end_str = event['end'].get('dateTime', event['end'].get('date'))
        event_start = datetime.fromisoformat(event_start_str).replace(tzinfo=pytz.utc)
        event_end = datetime.fromisoformat(event_end_str).replace(tzinfo=pytz.utc)

        if "block" in event.get('summary', '').lower():
            if event_start < shift_end and event_end > shift_start:
                return False  # There is an overlap with an existing event

    return True  # No overlaps found, the employee is available

def assign_shifts(shifts, emp_open, service, employees):
    total_shifts = sum(len(shifts[file]) - 1 for file in SHIFT_FILES)
    assigned_shifts = 0
    employee_queue = deque(range(1, len(emp_open)))  # Queue of employee indices, starting from 1 to skip header

    for shift_file in SHIFT_FILES:
        for shift in shifts[shift_file][1:]:  # Skip header row
            shift_date_str, _, shift_start_str, shift_end_str, _, shift_name = shift[:6]
            shift_date = datetime.strptime(shift_date_str, "%Y-%m-%d")
            weekday = shift_date.strftime('%A')
            shift_start = shift_date + timedelta(hours=int(shift_start_str.split(":")[0]), minutes=int(shift_start_str.split(":")[1]))
            shift_end = shift_date + timedelta(hours=int(shift_end_str.split(":")[0]), minutes=int(shift_end_str.split(":")[1]))
            shift_duration = float(shift[4])

            shift_assigned = False
            attempted_employees = set()

            while not shift_assigned and len(attempted_employees) < len(emp_open) - 1:
                index = employee_queue.popleft()  # Get the next employee in the queue
                attempted_employees.add(index)
                employee = emp_open[index]
                employee_name = employee[0]

                if (employees[index][2] == '1' and shift_file == "laser_shifts.csv") or \
                   (employees[index][3] == '1' and shift_file == "holo_shifts.csv"):
                    if is_employee_available(service, employees[index], shift_start, shift_end) and \
                       employee[2] >= shift_duration:
                        employee[1] += shift_duration  # Add to work_hours
                        employee[2] -= shift_duration  # Subtract from remaining_hours

                        shift[-1] = employee_name  # Assign employee name to shift
                        assigned_shifts += 1

                        print(f"{weekday}, {shift_date_str}, {shift_name} assigned to {employee_name}")
                        shift_assigned = True

                employee_queue.append(index)  # Re-add the employee to the end of the queue

                # If all employees have been attempted and shift is not assigned, mark shift as "OFFEN" and break
                if len(attempted_employees) == len(emp_open) - 1 and not shift_assigned:
                    shift[-1] = "OFFEN"
                    break

    print(f"Total shifts processed: {assigned_shifts}/{total_shifts}")



# Function to write data to CSV
def write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

## Main Program

def main():
    # Read shifts and employee data
    shifts = {file: read_csv(os.path.join(TMP_DIR, file)) for file in SHIFT_FILES}
    # print("Debug - Shifts dictionary content:", shifts)

    # Extract month and year from the first data row of either shift file
    first_shift_date_str = shifts['holo_shifts.csv'][1][0]  # Assuming the date is in the first column
    first_shift_date = datetime.strptime(first_shift_date_str, "%Y-%m-%d")
    shift_month = first_shift_date.month
    shift_year = first_shift_date.year

    employees = read_csv(EMPLOYEES_FILE)
    emp_open = prepare_employee_data(employees)  # Create emp_open data structure

    # Connect to Google Calendar
    service = google_calendar_service()

    # Fetch and write employee events
    fetch_and_write_employee_events(service, employees, shift_month, shift_year)

    # Assign shifts
    assign_shifts(shifts, emp_open, service, employees)

    # Write updated data back to CSV files
    for shift_file in SHIFT_FILES:
        month_name = calendar.month_name[shift_month].lower()
        output_file = os.path.join(
            OUTPUT_DIR, f"{shift_file.split('_')[0]}_{month_name}.csv")
        write_csv(output_file, shifts[shift_file])

    # Prepare and write employee output using emp_open data structure
    write_csv(os.path.join(OUTPUT_DIR, "emp_output.csv"), emp_open)

if __name__ == "__main__":
    main()

