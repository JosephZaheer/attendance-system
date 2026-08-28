import helper_functions as hf
import pandas as pd
import attendance 
import csv

while True:
    print("|——————————————————————————————————————|")
    print("|        AI ATTENDANCE SYSTEM          |")
    print("|——————————————————————————————————————|")
    print("|    0. Back / Exit Program            |")
    print("|    1. Mark Attendance                |")
    print("|    2. View Attendacnce Register      |")
    print("|    3. View total Attendance          |")
    print("|    4. Register Student               |")
    print("|    5. Remove Student                 |")
    print("|——————————————————————————————————————|")

    option = input("Choose option: ").strip()
    hf.load_animation()
    print()

    
    if option == "0":
        print("|——————————————————————————————————————|")
        print("|           Program Closed             |")
        print("|——————————————————————————————————————|")

        break
        
    elif option == "1": #mark student attendance
        pass
        #data = attendance.camera_capture()
        #prediction = model.predict(data)
        #attendance.mark_attendence(prediction)
            
    elif option == "2": #view attendance register for a specific date or month
        when = input("Enter (date month year) or (month year): ").strip("( )")

        if when == "0": #back
            continue

        hf.load_animation()

        attendance.view_attendance(when.split())
            
    elif option == "3": #view total of attendance and percentage

        #TODO: what happens when a student is removed mid year
        #csv files will be of different no. of rows
            
        when = input("Enter (month year) or (year) or (month-month-year): ").strip("( )")

        if when == "0":
            continue

        hf.load_animation()
        attendance.attendance_perc(when.split())
                
    elif option == "4": #register a student
        name = input("Enter name: ").title().strip()
        roll = input("Enter roll no.: ").strip()

        if "0" in (name, roll):
            continue

        hf.load_animation(newline=False)
            
        names_register = pd.read_csv("attendance_system/sample_register.csv")

        #might give syntax error or logical error >>>
        if (roll, name) in names_register:
            print("Student is already registered!")
            continue

        valid_name = name.replace(" ", "").isalpha()
        valid_roll = roll.isdigit()

        if valid_name and valid_roll:
            names_list = list(names_register["names"])

            #roll = index + 1
            names_list.insert(int(roll)-1, name)
            
            with open("attendance_system/sample_register.csv", "w") as file:
                writer = csv.writer(file)
                writer.writerow(["roll", "name"])
                    
                for index, name in enumerate(names_list):
                    writer.writerow([index+1, name.title()])

        else:
            print(f"Invalid Input: {valid_name=} {valid_roll=}")
                        
        attendance.camera_capture(name, True)
        print("Student registered!")
            
    elif option == "5": #remove a student
        name_or_roll = input("Enter student name or roll no.: ")
        name_or_roll = name_or_roll.strip().title()

        if when == "0":
            continue

        hf.load_animation()
        print("WARNING\n")
        print(f"Delete student record for {name=} {roll=}?\n")
        print("[Y] Yes\n[N] No")

        deletion_choice = input().strip()

        if deletion_choice.upper() == "Y":
            print()
            hf.load_animation("bar")
            attendance.remove_student(name_or_roll)
            
        elif deletion_choice.upper() == "N":
            print("Deletion cancelled")

        else:
            print("Invalid Input (cancelled deletion)")
            
    else: 
        print("Invalid Input")