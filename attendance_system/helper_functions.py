from pathlib import Path
import pandas as pd
import numpy as np
import time
import cv2
import csv
import sys

month_names = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
        
################################################################################

def camera_capture(name="", register=False, camera_index=0, max_frames=300, rescale=0.5):
    
    capture = cv2.VideoCapture(camera_index)
    no_of_frames = 0
    
    haar_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    while True:
        frame_taken, frame = capture.read()
        
        #if not is_true or no_of_frames >= max_frames or cv.waitKey(0.1) or 0xFF == ord("q"):
        
        no_of_frames += 1

        height = frame.shape[0]
        width = frame.shape[1]
        new_res = (int(width*rescale), int(height*rescale))
        
        resized = cv2.resize(frame, new_res, interpolation=cv2.INTER_AREA)
        blurred = cv2.GaussianBlur(resized, (1,1), cv2.BORDER_DEFAULT)
        grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

        #face_rect = face rectangle
        face_rects = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=10)

        #there many be multiple faces detected, we will only keep one (at index 0)
        face_rect = face_rects[0]
        x, y, w, h = face_rect
        cropped = grey[y:y+h, x:x+w]
            
        if register:
            cv2.imwrite(f"/dataset/{name}/Image{no_of_frames}.png", cropped)
            
        else:
            cv2.imwrite(f"/attendance/Image{no_of_frames}.png", cropped)
        
    capture.release()
    cv2.destroyAllWindows()

    return None
    
################################################################################
    
def mark_attendance(prediction):

    date, month, year = time.strftime("%d %B %Y").split()
    filepath = f"/attendance_{year}/attendance_{month}.csv"

    try:
        attendance_register = pd.read_csv(filepath)

    except FileNotFoundError:
        attendance_register = pd.read_csv("attendance_system/sample_register.csv")
    
    if not date in attendance_register.columns:
        attendance_register.loc[:, date] = "A"
    
    attendance_register.loc[prediction, date] = "P"            
    attendance_register.to_csv(filepath, index=False)
    
################################################################################

def view_attendance(when):
    if "".join(when) == "0": 
        return 0

    elif len(when) == 3:
        valid_date = when[0].isdigit() 
        valid_month = when[1].title() in month_names
        valid_year = when[0].isdigit()

        if valid_date and valid_month and valid_year:
            date, month, year = when[0], when[1].title(), when[2]

        else:
            print("Invalid Input")
            return None

    elif len(when) == 2:
        valid_month = when[0].title() in month_names
        valid_year = when[1].isdigit()

        if valid_month and valid_year:
            month, year = when[0].title(), when[1]

        else:
            print("Invalid Input")
            return None
                
    else:
        print("Invalid Input")
        return 0
            
    fancy_print("...", 0.35)
    print("\n")
                
    #filepath = f"/attendance_{year}/attendance_{month}.csv"
    filepath = f"/workspaces/attendance-system/attendance_system/attendance_{month}.csv"
                
    try:
        attendance_register = pd.read_csv(filepath)
                            
    except FileNotFoundError:
        print(f"No records available for {month} {year}")
        return None

    if len(when) == 3:
        print(attendance_register.loc[:, ("roll", "names", date)])

    else:
        print(attendance_register)
        
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
   
animations = {
    "dots": ("...", 0.5),
    "bar":  ("============", 0.3),
    "fill": ("████████████", 0.3),
    "empty": ("       ", 0.2)
}

def load_animation(indicator="dots", newline=True):

    print()
    s, time_per_char = animations[indicator]
    print("[", end="")

    for char in s:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(time_per_char)

    print("]", end="\n" if newline else "")

################################################################################
