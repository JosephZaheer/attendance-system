#import tensorflow as tf
import streamlit as st
import pandas as pd
import box_print
import time
import cv2
import csv

month_names = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]

class FaceRecognition:

    def __init__(self):
        pass
        #self.model = model

    def camera_capture(self, camera_index=0, max_frames=300, res=(224, 224)):
        haar_cascade = cv2.CascadeClassifier("attendance_system/haarcascade_frontalface_default.xml")
        capture = cv2.VideoCapture(camera_index)
        self.frames = []
        
        while True:
            success, frame = capture.read()

            if not success:
                st.write("Could not read from camera")
                break
                
            if len(self.frames) >= max_frames:
                break

            blurred = cv2.GaussianBlur(frame, (1,1), cv2.BORDER_DEFAULT)
            grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

            #there many be multiple faces detected, we will only keep one (at index 0)
            #haar cascade gives four points, which when connected, form a rectangle enclosing the face

            faces_detected = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=10)
            try:
                face_rectangle = faces_detected[0]
                x, y, w, h = face_rectangle
                cropped = grey[y:y+h, x:x+w]
                self.frames.append(cropped)        
            
            except Exception as e:
                st.write(e)
                pass

        capture.release()
        try: cv2.destroyAllWindows()
        except: pass

    def add_to_dataset(self, name):
        #or just train model here directly
        for idx, frame in enumerate(self.frames):
            cv2.imwrite(f"attendance_system/Dataset/{name}/train/Image{idx}.webp", frame)

    def mark_attendance(self):
        date, month, year = time.strftime("%d %B %Y").split()
        date = "0" + date

        filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"

        try:
            attendance_register = pd.read_csv(filepath)

        except FileNotFoundError:
            attendance_register = pd.read_csv("attendance_system/sample_register.csv")
    
        if not date in attendance_register.columns:
            attendance_register.loc[:, date] = "A"

        #prediction = self.model.predict(self.frames)
        #confidence = tf.nn.softmax(prediction)
        #attendance_register.loc[prediction, date] = "P"            
        #attendance_register.to_csv(filepath, index=False)
    
#Functions for general operations on attendance register

def view_attendance(when):

    #Check if input is valid :-
    #1. Follows correct format (date month year) or (month year)
    #2. Date and year are number, month is a real month

    if len(when) == 3 and when[0].isdigit() and (when[1].title() in month_names) and when[2].isdigit():
        format = "date month year"
        date, month, year = "0" + when[0], when[1].title(), when[2]

    elif len(when) == 2 and (when[0].title() in month_names) and when[1].isdigit():
        format = "month year"
        month, year = when[0].title(), when[1]
                
    else:
        print("Invalid Input")
        return None
            
    filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"

    try:
        attendance_register = pd.read_csv(filepath)
                            
    except FileNotFoundError:
        st.write(f"No records available for {month} {year}")
        return None

    if format == "date month year":
        if not str(date) in attendance_register.columns:
            st.write(f"Attendance not availabe for this {date=}")
            return None

        columns = ["roll", "name", date]

    else:
        columns = list(attendance_register.columns)

    st.dataframe(attendance_register)
    return None
        
    lines = []
    for idx in attendance_register.index:
            if format == "month year":
                line = list(attendance_register.loc[idx])
                line[0] = "  " + str(line[0]) + "  "
                line[1] = "  " + line[1] + "  "

            else:
                line = list(attendance_register.loc[idx, ("roll", "name", date)])

            lines.append(line)

    lines.insert(0, columns)
    print()                

def attendance_perc(when):    

    #Check :-
    #1. Follows correct format (month-month year) or (month year) or (year)
    #2. Date and year are number, month is a real month

    if len(when) == 3 and (when[0].title() in month_names) and (when[1].title() in month_names) and when[2].isdigit():
        year = when[2]                
        start = month_names.index(when[0].title())
        stop = month_names.index(when[1].title()) + 1
        months_list = [month for month in month_names[start:stop]]
                                
    elif len(when) == 2 and when[0].title() in month_names and when[1].isdigit():
        year = when[1]
        months_list = [when[0].title()]
            
    elif len(when) == 1 and when[0].isdigit():
        year = when[0]
        months_list = month_names
                    
    else:
        st.write("Invalid Input")
        return None
                
    total_sum = pd.read_csv("attendance_system/sample_register.csv")
    total_sum["sum"] = ""
    working_days = 0
                
    for month in months_list:
        filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"
                    
        try:
            attendance_register = pd.read_csv(filepath)
                        
        except FileNotFoundError:
            continue

        #attendance_register.columns = (roll, names, date, date, date, ...)
        working_days += len(attendance_register.columns) - 2
                    
        for column in attendance_register.columns[2:]:
            total_sum["sum"] += attendance_register[column]

    st.dataframe(total_sum)

    st.write(f"Working days = {working_days}\n")
    return None
            
    #total_sum.loc[idx, "sum"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    lines = []
    for idx, row in enumerate(total_sum["sum"]):
        total_sum.loc[idx, "sum"] = str(row.count("P"))
        total_sum.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"
        lines.append(list(total_sum.loc[idx]))

    lines.insert(0, list(total_sum.columns))
    box_print.box_print2D(lines, title=f" Attendance Total for {"-".join(when).title()} ", s=2, strip=False)
    st.write(f"Working days = {working_days}\n")
                            
def remove_student(name_or_roll):
        
    names = pd.read_csv("attendance_system/sample_register.csv")
        
    #Check if input is a name or a roll
    if name_or_roll.isdigit():
        name_or_roll = int(name_or_roll)
        index_remove = list(names[names["roll"]==name_or_roll].index)[0]
                
    elif name_or_roll.replace(" ", "").isalpha():                
        index_remove = list(names[names["name"]==name_or_roll].index)[0]
                
    else:
        st.write("Invalid Input")
        return None
                
    file = open("attendance_system/sample_register.csv", "w")
    writer = csv.writer(file)
    writer.writerow(["roll", "name"])
                
    removed = False
    for idx in names.index:
        if idx == index_remove:
            removed = True
            continue
                        
        row = list(names.loc[idx])
        if removed:
            row[0] -= 1
                        
        writer.writerow(row)
    file.close()
