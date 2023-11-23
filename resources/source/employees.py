import csv


def read_csv(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        return list(reader)


def write_csv(file_name, data):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def get_valid_input(prompt, valid_inputs):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in valid_inputs:
            return user_input
        else:
            print(f"Invalid input. Please enter {', '.join(valid_inputs)}.")


def add_employee():
    name = input("Name of the employee? ")
    cal_id = input("Google Calendar ID? ")
    laser = input(
        "Working at Lasertag? (True/False) ").lower() in ['true', 'yes', '1']
    holo = input(
        "Working at Holocafe? (True/False) ").lower() in ['true', 'yes', '1']
    max_hours = input("How much time does the employee have? ")
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
        emp_to_modify[2] = input(
            "Working at Lasertag? (True/False) ").lower() in ['true', 'yes', '1']
    elif modification_choice == 'd':
        emp_to_modify[3] = input(
            "Working at Holocafe? (True/False) ").lower() in ['true', 'yes', '1']
    elif modification_choice == 'e':
        emp_to_modify[4] = input("New MaxHours: ")


def delete_employee(employees):
    print("\n".join(f"{idx+1}. {emp[0]}" for idx, emp in enumerate(employees)))
    emp_num = int(get_valid_input("Enter the number of the employee to delete: ",
                                  [str(i) for i in range(1, len(employees) + 1)])) - 1
    del employees[emp_num]


def main():
    file_name = 'employees.csv'
    employees = read_csv(file_name)
    headers = employees.pop(0)

    while True:
        action = get_valid_input(
            "Do you want to add, modify or delete an employee from the list? (a) Add; (b) modify; (c) delete: ", ['a', 'b', 'c'])
        if action == 'a':
            employees.append(add_employee())
        elif action == 'b':
            modify_employee(employees)
        elif action == 'c':
            delete_employee(employees)

        continue_choice = get_valid_input(
            "Do you wish to change, add, or modify something else? (yes/no): ", ['yes', 'no'])
        if continue_choice == 'no':
            break

    employees.insert(0, headers)
    write_csv(file_name, employees)


if __name__ == "__main__":
    main()