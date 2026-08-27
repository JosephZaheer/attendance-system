import pandas as pd
import csv

n = pd.read_csv("attendance_April.csv")

#m.loc[:, :] = n.loc[:, ("roll", "names")]

#m.to_csv("student_names.csv")

with open("student_names.csv", "w") as f:
    
    w = csv.writer(f)
    r = w.writerow
    
    r(("roll", "names"))
    
    for i in n.index:
        
        row = list(n.loc[i])[:2]
        
        r(row)
        
