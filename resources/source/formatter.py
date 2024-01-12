import csv
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # Adjust the base path to go two levels up from the current script location
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_path, relative_path)

def read_csv(file_path):
    """ Read CSV and return rows as list of dictionaries """
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

def write_csv(file_path, fieldnames, data):
    """ Write data to a CSV file """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def is_time_overlap(shift, event):
    """ Check if event time overlaps with shift time """
    return shift['day'] == event['day'] and \
           max(shift['start'], event['start']) < min(shift['end'], event['end'])

# Read employee names
employees_file_path = resource_path('resources/data/employees.csv')
employees = [row['name'] for row in read_csv(employees_file_path)]

# Read shift data and add a new column for free employees
laser_shifts_file_path = resource_path('tmp/laser_shifts.csv')
holo_shifts_file_path = resource_path('tmp/holo_shifts.csv')
laser_shifts = read_csv(laser_shifts_file_path)
holo_shifts = read_csv(holo_shifts_file_path)
for shift in laser_shifts + holo_shifts:
    shift['free employees'] = ''

# Process employee availabilities
for employee in employees:
    employee_events_file_path = resource_path(f'tmp/{employee}_events.csv')
    employee_events = read_csv(employee_events_file_path)
    for shift in laser_shifts + holo_shifts:
        for event in employee_events:
            if is_time_overlap(shift, event) and 'block' not in event['shift'].lower():
                # Add the employee's name with a separator
                shift['free employees'] += (employee + '/') if shift['free employees'] else (employee + '/')

# Combine and export data
combined_shifts = laser_shifts + [{}] + holo_shifts  # Empty dictionary represents an empty row
fieldnames = laser_shifts[0].keys()  # Assuming both laser and holo shifts have the same columns
output_file_path = resource_path('output/free_employees.csv')
write_csv(output_file_path, fieldnames, combined_shifts)

print("Shift planning data processed and saved.")
