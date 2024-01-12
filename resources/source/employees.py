import csv
import os
import sys

## 01.12.2023 

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Set Base directory # Initialize CSV file
ScriptPath = os.path.abspath(__file__)
HomeDir = os.path.dirname(os.path.dirname(os.path.dirname(ScriptPath)))
csvPath = resource_path(os.path.join('..', 'data', 'employees.csv'))
print("CSV Path:", csvPath)

## Functions

def read_csv(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

def write_csv(file_name, data):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def get_boolean_input(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['true', 'yes', '1']:
            return '1'
        elif user_input in ['false', 'no', '0']:
            return '0'
        elif user_input == 'x':
            print("Exiting program.")
            sys.exit()
        else:
            print("Invalid input. Please enter true/false or 'x' to exit.")

def get_valid_input(prompt, valid_inputs):
    valid_inputs.append('x')  # Add 'x' as a valid input for exiting
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == 'x':
            print("Exiting program.")
            sys.exit()  # Exit the program
        elif user_input in valid_inputs:
            return user_input
        else:
            print(f"Invalid input. Please enter {', '.join(valid_inputs[:-1])} or 'x' to exit.")

def add_employee():
    name = input("Name of the employee? ")
    if name.lower() == 'x':
        print("Exiting program.")
        sys.exit()
    cal_id = input("Google Calendar ID? ")
    if cal_id.lower() == 'x':
        print("Exiting program.")
        sys.exit()
    laser = get_boolean_input("Working at Lasertag? (True/False) ")
    holo = get_boolean_input("Working at Holocafe? (True/False) ")
    max_hours = input("How much time does the employee have? ")
    if max_hours.lower() == 'x':
        print("Exiting program.")
        sys.exit()
    return [name, cal_id, laser, holo, max_hours]


def modify_employee(employees):
    print("\n".join(f"{idx+1}. {emp[0]}" for idx, emp in enumerate(employees)))
    emp_num = int(get_valid_input("Enter the number of the employee to modify: ",
                                  [str(i) for i in range(1, len(employees) + 1)])) - 1
    emp_to_modify = employees[emp_num]

    modification_choice = get_valid_input("What do you want to change? (a) Name; (b) Calendar-ID; (c) Lasertag; (d) Holo; (e) MaxHours: ",
                                          ['a', 'b', 'c', 'd', 'e'])
    if modification_choice == 'a':
        emp_to_modify[0] = input("New Name: ")
    elif modification_choice == 'b':
        emp_to_modify[1] = input("New Google Calendar ID: ")
    elif modification_choice == 'c':
        emp_to_modify[2] = get_boolean_input("Working at Lasertag? (True/False) ")
    elif modification_choice == 'd':
        emp_to_modify[3] = get_boolean_input("Working at Holocafe? (True/False) ")
    elif modification_choice == 'e':
        emp_to_modify[4] = input("New MaxHours: ")

def delete_employee(employees):
    print("\n".join(f"{idx+1}. {emp[0]}" for idx, emp in enumerate(employees)))
    emp_num_input = get_valid_input("Enter the number of the employee to delete or 'x' to exit: ",
                                    [str(i) for i in range(1, len(employees) + 1)])

    if emp_num_input.lower() == 'x':
        print("Exiting program.")
        sys.exit()

    emp_num = int(emp_num_input) - 1
    del employees[emp_num]

##Main

def main():
    # Use the global csvPath variable
    employees = read_csv(csvPath)
    headers = employees.pop(0) if employees else ['name', 'cal-id', 'laser', 'holo', 'max_hours']

    while True:
        action = get_valid_input("\n\nDo you want to add, modify or delete an employee from the list? (a) Add; (b) modify; (c) delete; (x) exit: ", ['a', 'b', 'c'])
        if action == 'a':
            employees.append(add_employee())
        elif action == 'b':
            modify_employee(employees)
        elif action == 'c':
            delete_employee(employees)

        continue_choice = get_valid_input("Do you wish to change, add, or modify something else? (yes/no): ", ['yes', 'no'])
        if continue_choice == 'no':
            break

    employees.insert(0, headers)
    write_csv(csvPath, employees)

if __name__ == "__main__":
    main()
