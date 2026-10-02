import face_recognition as fr
import streamlit as st
import pandas as pd
import csv

month_names = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

year_list = pd.read_json("attendance_system/year_list.json")

def view_attendance():
    month = st.selectbox("Select a month:", month_names)
    year = st.selectbox("Select a year:", year_list)

    filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"

    try:
        register = pd.read_csv(filepath)
                            
    except FileNotFoundError:
        st.write(f"No records available for {month} {year}")
        return None

    date = st.slider("Choose a date: (0 for whole month)", min_value=0, max_value=31, step=1)
    date = str(date)

    if date.isdigit():
        if len(date) == 1 and date[0] != "0":
            date = "0" + date
        elif len(date) > 1 and date[0] == "0":
            date = date.lstrip("0")

    if date == "0":
        columns = list(register.columns)
        working_days = len(columns) - 2
        st.write(f"Working days: {working_days}")

    else:
        if date in register.columns:
            columns = ["roll", "name", date]

        else:
            st.write(f"Attendance not availabe for this date: {date}")
            return None

    register = register[columns]
    st.dataframe(register)
    
def percentage():    
    options = [
        "Range of months",
        "Whole year",
        "One month"]

    choice = st.selectbox("Choose an option:", options)

    year = st.selectbox("Select a year:", year_list)

    if choice == options[0]:
        start_month = st.selectbox("Select starting month:", month_names, key="month1")
        start = month_names.index(start_month)

        idx = month_names.index(start_month)

        stop_month = st.selectbox("Select ending month:", month_names[idx: ], key="month2")
        stop = month_names.index(stop_month) + 1

        months_list = [month for month in month_names[start:stop]]

    elif choice == options[1]:
        months_list = month_names

    else:
        month = st.selectbox("Select a month:", month_names, key="month3")
        months_list = [month]

    sum_register = pd.read_csv("attendance_system/sample_register.csv")
    sum_register["sum"] = ""
    working_days = 0
                
    for month in months_list:
        filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"
                    
        try:
            register = pd.read_csv(filepath)
                        
        except FileNotFoundError:
            continue

        #attendance_register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            sum_register["sum"] += register[column]
            
    #total_sum.loc[idx, "sum"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(sum_register["sum"]):
        sum_register.loc[idx, "sum"] = str(row.count("P"))
        sum_register.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"

    st.write(f"Working days: {working_days}")
    st.dataframe(sum_register)

def register_student(input_name, input_roll):
    #check if name and roll are valid

    valid_name = input_name.replace(" ", "").isalpha()
    valid_roll = input_roll.isdigit()        

    if not (valid_name and valid_roll):
            st.write("Invalid Input")
            return None

    names_register = pd.read_csv("attendance_system/sample_register.csv")
    names_list = list(names_register["name"])

    #roll = index + 1
    if input_roll in names_register["roll"] and input_name == names_list[int(input_roll) - 1]:
        st.write("Student already registered!")
        return None

    records = []
    for i in range(len(names_list)):
        roll = int(names_register.iloc[i, 0])
        name = names_register.iloc[i, 1]
        records.append((roll, name))

    records.append((int(input_roll), input_name))
    records.sort()

    with open("attendance_system/sample_register.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["roll", "name"])
                    
        for roll, name in records:
            writer.writerow([roll, name.title()])

    st.write("Registration Successful!")
    names_register = pd.read_csv("attendance_system/sample_register.csv")
    st.dataframe(names_register)
                            
def remove_student(name_or_roll):
    names = pd.read_csv("attendance_system/sample_register.csv")
        
    #Check if input is a name or a roll
    if name_or_roll.isdigit():# and int(name_or_roll) in tuple(names["roll"]):
        name_or_roll = int(name_or_roll)
        index_remove = list(names[names["roll"] == name_or_roll].index)[0]
                
    elif name_or_roll.replace(" ", "").isalpha():# and name_or_roll in tuple(names["name"]):                
        index_remove = list(names[names["name"] == name_or_roll].index)[0]
                
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

    st.write("Deletion Successful!")
    names_register = pd.read_csv("attendance_system/sample_register.csv")
    st.dataframe(names_register)

#_______________STREAMLIT MENU_______________

st.title("AI ATTENDANCE SYSTEM")
options = [
    "Mark Attendance",
    "View Attendance Register",
    "View Total Attendance",
    "Register Student",
    "Remove Student"
    ]

status = st.radio("Choose an operation:", options, key="Options")

if status == options[0]: #mark attendance
    #fr.mark_attendance()
    pass
            
elif status == options[1]: #view attendance register for a specific date or month
    view_attendance()
            
elif status == options[2]: #view attendance total and percentage            
    percentage()
                
elif status == options[3]: #register a student
    name = st.text_input("Enter student name:", key="Input03")
    name = name.strip().title()

    roll = st.text_input("Enter roll number:", key="Input04")
    roll = roll.strip()

    if name and roll:
        register_student(name, roll)

elif status == options[4]: #remove a student
    name_or_roll = st.text_input("Enter student name OR roll number:", key="Input05")
    name_or_roll = name_or_roll.strip().title()

    if name_or_roll:
        st.write("WARNING")
        Y_or_N = st.radio("Delete student record?", ("None", "No", "Yes"), key="Input06")

        if Y_or_N == "Yes":
            remove_student(name_or_roll)

        elif Y_or_N == "No":
            st.write("Deletion cancelled")

            
