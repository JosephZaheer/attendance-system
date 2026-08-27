from helper_functions import delay_print
import helper_functions
import pandas as pd
import time
import csv
import sys

helper_functions.fancy_intro()

while True:
    print(); delay_print("    ")
    print("0. Back / Exit program"); delay_print("    ")
    print("1. Mark attendance"); delay_print("    ")
    print("2. View attendance register"); delay_print("    ")
    print("3. Find attendance percentage"); delay_print("    ")
    print("4. Register student"); delay_print("    ")
    print("5. Remove student"); delay_print("    ")
    print()
    
    choice = input("choice: ").strip()
    print()
    
    match (choice):
        
        case "0":
            delay_print("...", 0.35)
            print("Program closed")
            break
        
        case "1":
            helper_functions.mark_attendence()
            
        case "2":
            print("Enter (date month year) or (month year): ", end="")
            when = input().strip("( )").split()
            
            helper_functions.view_attendance(when)
            
        case "3":
            #TODO: what happens when a student is removed mid year
            #csv files will be of different no. of rows
            
            print("Enter (month year) or (year) or (month-month year): ", end="")
            when = input().strip("( )").replace("-", " ").split()
            
            helper_functions.attendance_perc(when)
                
        case "4":
            name = input("Enter name: ")
            roll = int(input("Enter roll no.: "))
            
            names = pd.read_csv("student_names.csv")
            
            if name not in names:
                names_list = list(names["names"])
                names_list.insert(roll-1, name)
            
                with open("student_names.csv", "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["roll", "names"])
                    
                    for idx, name in enumerate(names_list):
                        writer.writerow([idx+1, name])
                        
            helper_functions.camera_capture(name, True)
            
        case "5":
            name_or_roll = input("Enter student name or roll no.: ")
            name_or_roll = name_or_roll.strip().title()
            
            helper_functions.remove_student(name_or_roll)
            
        case _:
            print("Invalid Input")