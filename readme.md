# Ultimate Shift Planner
## about
Tool to retrieve shifts and employees availabilities from Google Calendars

## Manual:
# Run the UltimateShift

1. Run UltimateShiftPlanner.exe from /dist
2. Choose the option you need and follow the instructions.
3. 

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

# Optimization shiftplanner

    Centralize Configuration and Paths:
    Consider using a configuration file or a centralized class for configurations. This approach makes it easier to manage paths and settings, and it separates configuration management from business logic.

    Error Handling and Logging:
    Implement more robust error handling, especially around file operations and API calls. Consider using Python's logging module instead of print statements for better logging management.

    Function Decomposition:
    Some functions, like fetch_and_write_employee_events, are doing multiple things (fetching data and writing to a file). It might be beneficial to decompose such functions into smaller, single-responsibility functions.

    Optimize File Reading:
    The read_csv function reads the entire file into memory, which might not be efficient for very large files. Consider reading and processing the file line by line if you expect to handle large data sets.

    Use of Global Variables:
    The script uses global variables (like SHIFT_FILES, EMPLOYEES_FILE). While this is not inherently bad, be cautious about overusing global variables, as they can make the code harder to manage and test.

    Data Processing Efficiency:
    In the assign_shifts function, there are nested loops which could become a performance bottleneck with large datasets. Consider optimizing this part, maybe by preprocessing some data or using more efficient data structures like dictionaries for faster lookups.

    Code Reusability:
    Look for patterns or repeated code blocks that could be turned into reusable functions or modules. This enhances maintainability and reduces the likelihood of bugs.

    Use Pythonic Conventions:
    Adhere to Pythonic conventions and idioms. For instance, list comprehensions can sometimes replace loops for more concise and readable code.

    Documentation and Comments:
    Add docstrings to functions, explaining their purpose, parameters, and return values. This practice is beneficial for maintenance and for any new developers who might work with your code.

    Testing and Validation:
    Consider adding unit tests, especially for the core logic parts. Testing ensures your code behaves as expected and makes it safer to refactor or optimize parts of your script in the future.