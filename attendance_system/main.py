import face_recognition as fr
import streamlit as st
import pandas as pd
import pickle
import csv

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
st.write("#"*50)
st.write(BASE_DIR)
st.write("#"*50)

month_names = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

register_path = "sample_register.csv"

with open("attendance_system/years.dat", "rb") as f:
    year_list = pickle.load(f)

def view_attendance(month, year):
    data_path = f"/attendance_dataset/attendance_{year}/attendance_{month}.csv"

    try:
        register = pd.read_csv(data_path)
                            
    except FileNotFoundError:
        st.write(f"No records available for {month} {year}")
        return None

    date = st.slider("Specify a date: (0 for whole month)", min_value=0, max_value=31, step=1)

    if date == 0:
        columns = list(register.columns)

    else:
        if str(date) in register.columns:
            columns = ["roll", "name", str(date)]

        else:
            st.write(f"Attendance not availabe for this date: {date}")
            return None

    register = register[columns]
    register = register.set_index(register["roll"])
    register = register.drop("roll", axis=1)
    st.dataframe(register)

def percentage():    
    options = [
        "Range of months",
        "Whole year",
        "One month"
        ]

    choice = st.selectbox("Choose an option:", options)
    year = st.selectbox("Select a year:", year_list)

    if choice == options[0]: #range of months
        start_month = st.selectbox("Select starting month:", month_names, key="month1")
        start = month_names.index(start_month)

        stop_month = st.selectbox("Select ending month:", month_names[start:], key="month2")
        stop = month_names.index(stop_month) + 1

        months_list = [month for month in month_names[start:stop]]

    elif choice == options[1]: #whole year
        months_list = month_names

    else: #one specific month
        month = st.selectbox("Select a month:", month_names, key="month3")
        months_list = [month]

    students = pd.read_csv(register_path)
    students["Total"] = ""
    working_days = 0
                
    for month in months_list:
        data_path = f"/attendance_dataset/attendance_{year}/attendance_{month}.csv"
                    
        try:
            register = pd.read_csv(data_path)
                        
        except FileNotFoundError:
            continue

        #attendance_register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            students["Total"] += register[column]
            
    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(students["Total"]):
        students.loc[idx, "Total"] = str(row.count("P"))
        students.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"

    st.write(f"Working days: {working_days}")
    students = students.set_index(students["roll"])
    students = students.drop("roll", axis=1)
    st.dataframe(students)

def register_student(input_name, input_roll):
    input_name = input_name.title().strip()

    #check if name is valid
    if not input_name.replace(" ", "").isalpha():
            st.write("Invalid Input")
            return None

    register = pd.read_csv(register_path)
    names_list = list(register["name"])

    #roll = index + 1
    if input_roll in register["roll"] and input_name == names_list[input_roll - 1]:
        st.write("Student already registered!")
        return None

    records = []
    for i in range(len(names_list)):
        roll = int(register.iloc[i, 0])
        name = register.iloc[i, 1]
        records.append((roll, name))

    #records = [(roll, name), (roll, name), (roll, name), ...]
    #by sorting, all records are arranged sequentially according to the roll numbers
    records.append((int(input_roll), input_name))
    records.sort()

    with open(register_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["roll", "name"])
                    
        for roll, name in records:
            writer.writerow([roll, name.title()])

    st.write("Registration Successful!")
    register = pd.read_csv(register_path)
    register = register.set_index(register["roll"])
    register = register.drop("roll", axis=1)
    st.dataframe(register)
                            
def remove_student(index_remove):
    file = open(register_path, "w")
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
    names_register = pd.read_csv(register_path)
    names_register = names_register.set_index(names_register["roll"])
    names_register = names_register.drop("roll", axis=1)
    st.dataframe(names_register)

#_______________STREAMLIT MENU_______________

st.title("AI ATTENDANCE SYSTEM")
options = [
    "Home",
    "Mark Attendance",
    "View Attendance Register",
    "View Total Attendance",
    "Register Student",
    "Remove Student"
    ]

status = st.sidebar.radio("Choose an operation:", options, key="Options")

if status == options[0]:
    st.write("""Welcome to The Attendance System

    Purpose:

    The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
    this reduces the responsibilities of the teacher and gives them more room to breathe before classes began.

    Working:

    - Images are collected on which classification is done, the collection is through streamlit's camera_input()
    - Some preprocessing is done before classification to improve accuracy.
    - Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade 
    - The classification model to recognise the identity of students is a CNN model. It uses adam as the optimizer, sparse binary crossentropy for loss and has total ... parameters.
    - Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Panda's DataFrames.

    Made by:
    
    - Arush (Data Expert)
    - Aryan Vishwakarma (Video Producer)
    - Jaffar (Information Researcher)
    - Krishna V. Gupta (Communication Leader)
    - Yusuf Zaheer (Main Coder)
    - Zoheb Arsh (Web Designer)
    """)


elif status == options[1]: #mark attendance
    #student = image_select("Choose an image to classify: Aryan/Jaffar/Zoheb", images, captions=["Aryan", "Jaffar", "Zoheb"])

    img = st.camera_input("Take a photo: ")

    if img:
        st.write("Capture successful!")
        fr.mark_attendance(img, "model1")
            
elif status == options[2]: #view attendance register for a specific date or month
    month = st.selectbox("Select a month:", month_names)
    year = st.selectbox("Select a year:", year_list)

    if month and year:
        view_attendance(month, year)
            
elif status == options[3]: #view attendance total and percentage            
    percentage()
                
elif status == options[4]: #register a student
    name = st.text_input("Enter student name:", key="Input03")
    name = name.strip().title()

    roll = st.slider("Enter roll number:", min_value=1, max_value=38, step=1, key="Input04")


    if name and roll and st.button("Register"):
        register_student(name, roll)

elif status == options[5]: #remove a student
    names = pd.read_csv(register_path)
    names_list = list(names["name"])
    name = st.selectbox("Select a student:", names_list)                
    index_remove = names_list.index(name)

    if st.button("Delete"):
        remove_student(index_remove)


            
