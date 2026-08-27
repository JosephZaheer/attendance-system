from pathlib import Path
import pandas as pd
import numpy as np
import cv2 as cv
import time
import csv
import sys

month_names = ["January", "February", "March", "April", "May", "June",
"July", "August", "September", "October", "November", "December"]

################################################################################

def delay_print(s = "", t = 0.06):
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(t)
        
################################################################################

def camera_capture(name="", register=False):
    
    capture = cv.VideoCapture("Man1.mp4")
    no_of_frames = 0
    rescale_factor = 0.75
    
    haar_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    while True:
        is_true, frame = capture.read()
        
        if not is_true or no_of_frames >= 300 or cv.waitKey(0.1) or 0xFF == ord("q"):
            break
        
        no_of_frames += 1
        new_res = (
        int(frame.shape[1]*rescale_factor), 
        int(frame.shape[0]*rescale_factor))
        
        frame = cv.resize(frame, new_res, interpolation=cv.INTER_AREA)
        blurred = cv.GaussianBlur(frame, (1,1), cv.BORDER_DEFAULT)
        grey = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
        
        face_rect = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=10)
        face = face_rect[0]
        
        x, y, w, h = face
        cropped = grey[y:y+h, x:x+w]
            
        if register:
            cv.imwrite(f"/dataset/{name}/Image{no_of_frames}.png", cropped)
            
        else:
            cv.imwrite(f"/attendance/Image{no_of_frames}.png", cropped)
        
    capture.release()
    cv.destroyAllWindows()
    
################################################################################
    
def mark_attendance():
    
    camera_capture()
    #somehow import model

    prediction = model.predict(frames)
#prediction is a number. map to roll number

#use prediction to mark attendance

    date, month, year = time.strftime("%d %B %Y").split()

    filepath = Path(f"/attendance_{year}/attendance_{month}.csv")

    if not filepath.exists():
        with open(filepath, "w") as f:
        
            names = pd.read_csv("student_names.csv")
            names_list = list(names["names"])
        
            writer = csv.writer(f)
            writer.writerow(["roll", "names"])
        
            for i in names.index:
                writer.writerow([i+1, names_list[i]])
    
    attendance_register = pd.read_csv(filepath)
    
    if not date in attendance_register.columns:
        attendance_register.loc[:, date] = "A"
    
    attendance_register.loc[prediction, date] = "P"

    attendance_register.to_csv(path)
    
################################################################################

def view_attendance(when):
    if len(when) == 1 and when[0] == "0":
        return 0
                
    elif len(when) == 3 and (when[0]+when[2]).isdigit() and when[1].title() in month_names:
        date, month, year = when[0], when[1].title(), when[2]
                
    elif len(when) == 2 and when[0].title() in month_names and when[1].isdigit():
        month, year = when[0].title(), when[1]
                
    else:
        print("Invalid Input")
        return 0
            
    delay_print("...", 0.35)
    print("\n")
                
            #filepath = f"/attendance_{year}/attendance_{month}.csv"
    filepath = f"attendance_{month}.csv"
                
    try:
        attendance_register = pd.read_csv(filepath)
                
        if len(when) == 3:
            print(attendance_register.loc[:, ("roll", "names", date)])
                    
        else:
            print(attendance_register)
            
    except FileNotFoundError:
        print(f"No records available for {month} {year}")
        
################################################################################
                
def attendance_perc(when):
    if len(when) == 1 and when[0] == "0":
        return 0
                
    elif (len(when) == 3 and when[0].title() in month_names
    and when[1].title() in month_names
    and when[2].isdigit()):
                
        year = when[2]                
        start = month_names.index(when[0].title())
        stop = month_names.index(when[1].title()) + 1
        months_list = []
                
        for i in range(start, stop):
            months_list.append(month_names[i])
                
    elif (len(when) == 2 and when[0].title() in month_names
    and when[1].isdigit()):
                
        year = when[1]
        months_list = [when[0].title()]
            
    elif len(when) == 1 and when[0].isdigit():
                    
        year = when[0]
        months_list = month_names
                    
    else:
        print("Invalid Input")
        return 0
                
    names = pd.read_csv("student_names.csv").loc[:, ("roll","names")]
    month_sum_df = pd.DataFrame()
    working_days = 0
                
    for month in months_list:
                #filepath = f"/attendance_{year}/attendance_{month}.csv"
        filepath = f"attendance_{month}.csv"
                    
        try:
            attendance_register = pd.read_csv(filepath)
                        
        except FileNotFoundError:
            break
                        
        working_days += len(attendance_register.columns) - 2
                    
        for column in attendance_register.columns:
            attendance_register.loc[
            attendance_register[column]=="A", column] = 0
                        
            attendance_register.loc[
            attendance_register[column]=="P", column] = 1
                        
        del attendance_register["roll"]
        del attendance_register["names"]
                    
        sum = attendance_register.sum(axis=1)
        month_sum_df = pd.concat([month_sum_df, sum], axis=1)
                
    sum = month_sum_df.sum(axis=1)
    per = sum.apply(lambda x: f"{x*100/working_days:.0f}%")
    df = pd.concat([names, sum, per], axis=1)
    df.rename(columns={0: 'sum', 1: 'percentage'}, inplace=True)
                
    delay_print("...", 0.35)
    print("\n")
    print(df)
    print(f"Working days = {working_days}")
    
################################################################################
    
def remove_student(name_or_roll):
    if name_or_roll == "0":
        return 0
        
    names = pd.read_csv("student_names.csv")
            
    if name_or_roll.isdigit():
        name_or_roll = int(name_or_roll)
        index_remove = list(
        names[names["roll"]==name_or_roll].index)[0]
                
    elif name_or_roll.replace(" ", "").isalpha():                
        index_remove = list(
        names[names["names"]==name_or_roll].index)[0]
                
    else:
        print("Invalid Input")
        return 0
        
    removed = False
                
    f = open("student_names.csv", "w")
    writer = csv.writer(f)
    writer.writerow(["roll", "names"])
                
    for i in names.index:
        if i == index_remove:
            removed = True
            continue
                        
        row = list(names.loc[i])
                    
        if removed:
            row[0] -= 1
                        
        writer.writerow(row)
                        
    f.close()

################################################################################

hashes = "##############################################################################"

def fancy_intro():
    print(hashes)
    print("                        ", end="")
    sys.stdout.flush()
    time.sleep(0.5)
    print("ATTENDANCE   ", end="")
    sys.stdout.flush()
    time.sleep(0.5)
    print("SYSTEM")
    sys.stdout.flush()
    time.sleep(0.5)
    print(hashes)
    
################################################################################
   