import pandas as pd
import attendance 
import box_print
import csv

#the file "attendance_cnn_model.keras" does not exist yet
#it will be created once model has been finished and trained on student dataset
face_recognizer = attendance.FaceRecognition("attendance_cnn_model.keras")

title = "AI ATTENDANCE SYSTEM"
options = [

    "0. Back / Exit Program",
    "1. Mark Attendance",
    "2. View Attendance Register",
    "3. View Total Attendance",
    "4. Register Student",
    "5. Remove Student"
]

while True:
    box_print.box_print(options, title=title)
    option = input("Choice: ").strip()
    print()

    if option == "0":
        box_print.box_print(["Program Closed"])
        break
        
    elif option == "1": #mark attendance
        continue
        face_recognizer.camera_capture()
        face_recognizer.mark_attendance()
            
    elif option == "2": #view attendance register for a specific date or month
        when = input("Enter (date month year) or (month year): ").strip("( )")
        print()
        
        if when == "0": #back
            continue

        when = when.split()
        attendance.view_attendance(when)
            
    elif option == "3": #view attendance total and percentage            
        when = input("Enter (month year) or (year) or (month-month year): ").strip("( )")
        print()

        if when == "0":
            continue

        when = when.replace("-", " ").split()
        attendance.attendance_perc(when)
                
    elif option == "4": #register a student
        input_name = input("Enter name: ").strip().title()
        input_roll = input("Enter roll no.: ").strip()

        if "0" in (input_name, input_roll):
            continue

        #check if name and roll are valid
        if not (input_name.replace(" ", "").isalpha() and input_roll.isdigit()):
            print("Invalid Input")
            continue

        names_register = pd.read_csv("attendance_system/sample_register.csv")
        names_list = list(names_register["name"])

        #roll = index + 1
        if input_name == names_list[int(input_roll) - 1]:
            print("Student already registered!")
            continue

        names_list.insert(int(input_roll)-1, input_name)
            
        with open("attendance_system/sample_register.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
                    
            for idx, name in enumerate(names_list):
                writer.writerow([idx+1, name.title()])

        continue              
        face_recognizer.camera_capture()
        face_recognizer.add_to_dataset(input_name)
        print("Student registered!")
            
    elif option == "5": #remove a student
        name_or_roll = input("Enter student name or roll no.: ").strip().title()

        if name_or_roll == "0":
            continue
        
        print("WARNING\n")
        print("Delete student record?\n")
        print("[Y] Yes\n[N] No")

        Y_or_N = input().strip().upper()
        print()

        if Y_or_N == "Y":
            attendance.remove_student(name_or_roll)
            print("Student removed")
            
        else:
            print("Deletion cancelled")
            
    else: 
        print("Invalid Input")