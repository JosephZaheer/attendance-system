import pandas as pd
import random as rn
import os

data = {
    
    "roll": (1,2,3,4,5,6),
    "name": ("Aryan", "Arush", "Jaffar", "Krishna", "Yusuf", "Zoheb Arsh")}
    
months = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December"]

year = 2026

for month in months:
    for i in range(1, 30):
        l = []
        for j in range(6):
            attendance = rn.randint(0,1)
        
            if attendance == 0:
                l.append("A")
            
            else:
                l.append("P")
            
        data[i] = tuple(l)
    
    df = pd.DataFrame(data)


    if not os.path.isdir(f"/workspaces/attendance-system/attendance_system/attendance_dataset/attendance_{year}"):
        os.mkdir(f"/workspaces/attendance-system/attendance_system/attendance_dataset/attendance_{year}")

    df.to_csv(f"/workspaces/attendance-system/attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv", index=False)