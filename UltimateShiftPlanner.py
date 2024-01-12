import os
import sys
import subprocess
from resources.source import shiftplanner, Retrieve_Shifts, employees


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def run_script(script_name):
    script_path = resource_path(os.path.join('resources', 'source', script_name))
    if os.path.isfile(script_path):
        print(f"Running script: {script_path}")
        subprocess.run(['python', script_path], check=True)
    else:
        print("Script not found.")

def main():
    while True:
        print("### Ultimate Shift Planner ###\n")
        print("Choose a function:")
        print("1) Schichten für Monat ziehen")
        print("2) Schichten für aktuell gewählten Monat erstellen")
        print("3) Tabelle \"Freie Mitarbeiter\" erstellen")
        print("4) Mitarbeiter ändern")
        print("x) UltimateShiftPlanner beenden\n")

        choice = input("Enter your choice: ").lower()

        if choice in ['1', 'one', 'eins', 'a']:
            run_script('Retrieve_Shifts.py')
        elif choice in ['2', 'two', 'zwei', 'b']:
            run_script('shiftplanner.py')
        elif choice in ['3', 'three', 'drei', 'c']:
            run_script('formatter.py')
        elif choice in ['4', 'four', 'vier', 'd']:
            run_script('employees.py')
        elif choice in ['q', 'x', 'exit', 'quit', 'schließen', 'ende']:
            print("Exiting UltimateShiftPlanner.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
