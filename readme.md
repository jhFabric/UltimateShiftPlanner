# Ultimate Shift Planner
## about
Tool to retrieve shifts and employees availabilities from Google Calendars  

# Framework
## Python
pip / pytz
pip / google-auth
pip / google-api-python-client
pip / google-auth-httplib2
pip / python-dateutil


Google App Scripts  
Google Cloud Console  

## Infos
OAuth Code:                         " 814319120937-8tmsanosuhlsa6ufbqopjs1q8b6cserk.apps.googleusercontent.com "  
Google Cloud Console Mail:          " ultimate-shift-planning@ultimate-shift-planning.iam.gserviceaccount.com "

## ToDos

# Datenstructur LaserShifts besser verstehen

# Logik für Schichtverteilung

1. Gather Employee Data

    Availability: For each employee, have a list of dates and times when they are available.
    Maximum Hours: The maximum number of hours each employee can work in the month.

2. Understand Shift Requirements

    From your LaserShifts list, you know the timing and duration of each shift.

3. Algorithm to Assign Shifts

    Sort Shifts: Start with the earliest shifts in the month and move forward.
    Prioritize Fair Distribution: Try to distribute shifts so that no employee is significantly over- or under-worked compared to others.
    Match Availability: For each shift, look for available employees who haven't reached their maximum hours.
    Assign Shifts: Assign an employee to a shift if they are available and haven’t exceeded their maximum hours. If multiple employees are available, you may choose the one with the fewest hours so far.

4. Implement the Logic

    This could be done through a series of loops and conditionals in Python, or for more complex scenarios, consider optimization techniques or algorithms.

5. Consider Special Cases

    Overlapping Shifts: Ensure no employee is assigned overlapping shifts.
    Preferences: If employees have shift preferences, try to accommodate them where possible.
    Equal Opportunity: Ensure all employees get a chance to work preferred shifts or high-demand times.

6. Review and Adjust

    After the initial assignment, review the distribution. If some employees are under-utilized and others are overburdened, adjust the assignments accordingly.
