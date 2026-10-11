import face_recognition as fr
import streamlit as st
import pandas as pd
import time
import csv
import os

#base = "/mount/src/attendance-system/attendance_system/"
base = "/workspaces/attendance-system/attendance_system/"
sample_path = base + "sample_register.csv"

YEARS = []
folders = os.listdir(base + "attendance_dataset")
for folder in folders:
    YEARS.append(int(folder[-4:]))

YEARS.sort(reverse=True)
MONTHS = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]
           
#_______________USEFUL FUNCTIONS_______________

def view_attendance(month, year):
    try:
        register = pd.read_csv(base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv")
        
    except FileNotFoundError:
        st.error(f"No records available for {month} {year}")
        return None

    date = st.slider("Specify a date:", min_value=0, max_value=31, step=1)
    st.caption("Select 0 for whole month")

    if date == 0:
        columns = list(register.columns)
        
    else:
        if str(date) in register.columns:
            columns = ["roll", "name", str(date)]
            
        else:
            st.error(f"Attendance not availabe for this date: {date}")
            return None

    register = register[columns]
    register = register.set_index(register["roll"])
    register = register.drop("roll", axis=1)
    st.dataframe(register)

def percentage():    
    options = [
        "One month",
        "Range of months",
        "Whole year"
        ]

    choice = st.selectbox("Choose an option:", options, index=None)
    year = st.selectbox("Select a year:", YEARS)
    
    if choice == options[0]: #one specific month
        month = st.selectbox("Select a month:", MONTHS, key="month3")
        months = [month]

    elif choice == options[1]: #range of months
        col1, col2 = st.columns(2)
        
        with col1:
            start_month = st.selectbox("Select starting month:", MONTHS, key="month1")
            start = MONTHS.index(start_month)

        with col2:
            stop_month = st.selectbox("Select ending month:", MONTHS[start:], key="month2")
            stop = MONTHS.index(stop_month) + 1

        months = [month for month in MONTHS[start:stop]]
        
    elif choice == options[2]: #whole year
        months = MONTHS

    else:
        return None

    percent_register = pd.read_csv(sample_path)
    percent_register["Total"] = ""
    working_days = 0
                
    for month in months:
        data_path = base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv"
                    
        try:
            register = pd.read_csv(data_path)
                        
        except FileNotFoundError:
            continue

        #attendance_register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            percent_register["Total"] += register[column]

    if working_days == 0:
        st.error("No attendance for the given month(s).")
        return None
    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)
    for idx, row in enumerate(percent_register["Total"]):
        percent_register.loc[idx, "Total"] = str(row.count("P"))
        percent_register.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"

    st.write(f"Working days: {working_days}")
    percent_register = percent_register.set_index(percent_register["roll"])
    percent_register = percent_register.drop("roll", axis=1)
    st.dataframe(percent_register)

def register_student(input_name, input_roll):
    input_name = input_name.title().strip()

    #check if name is valid
    if not input_name.replace(" ", "").isalpha():
            st.write("Invalid Input")
            return None

    register = pd.read_csv(sample_path)
    names_list = list(register["name"])

    #roll = index + 1
    if input_roll in register["roll"] and input_name == names_list[input_roll - 1]:
        st.error("Student already registered!")
        return None

    records = []
    for i in range(len(names_list)):
        roll = int(register.iloc[i, 0])
        name = register.iloc[i, 1]
        records.append((roll, name))

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        video = st.file_uploader("Upload a video (indoors): ", type=["mp4", "mov"])
        if video:
            with open(base + f"Dataset/Videos/{input_name}1.mov", "wb") as f:
                f.write(video.getbuffer())

            fr.camera_capture(input_name.title(), base + f"/video_dataset/{input_name}1.mov")

    with col2:
        video = st.file_uploader("Upload a video (somewhere else indoors): ", type=["mp4", "mov"])
        if video:
            with open(base + f"Dataset/Videos/{input_name}2.mov", "wb") as f:
                f.write(video.getbuffer())

            fr.camera_capture(input_name.title(), base + f"/video_dataset/{input_name}2.mov")

    with col3:
        video = st.file_uploader("Upload a video (outdoors): ", type=["mp4", "mov"])
        if video:
            with open(base + f"Dataset/Videos/{input_name}3.mov", "wb") as f:
                f.write(video.getbuffer())

            fr.camera_capture(input_name.title(), base + f"/video_dataset/{input_name}3.mov")        

    #records = [(roll, name), (roll, name), (roll, name), ...]
    #by sorting, all records are arranged sequentially according to the roll numbers
    records.append((int(input_roll), input_name))
    records.sort()

    if not st.button("**Register**"):
        return None

    st.divider()

    with open(sample_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["roll", "name"])
                    
        for roll, name in records:
            writer.writerow([roll, name.title()])

    st.success("Registration Successful!")
    register = pd.read_csv(sample_path)
    register = register.set_index(register["roll"])
    register = register.drop("roll", axis=1)
    st.dataframe(register)
                            
def remove_student(index_remove):
    file = open(sample_path, "w")
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

    st.success("Deletion Successful!")
    names_register = pd.read_csv(sample_path)
    names_register = names_register.set_index(names_register["roll"])
    names_register = names_register.drop("roll", axis=1)
    st.table(names_register)

#_______________STREAMLIT MENU_______________

st.title(":blue[AI ATTENDANCE SYSTEM]")
st.divider()

options = [
    "Home",
    "Mark Attendance",
    "View Attendance",
    "Total Attendance",
    "Make Changes",
    "New Student",
    "Remove Student"
    ]

day, date, month, year = time.strftime("%A %d %B %Y").split()
text = f"""It's **{day}**,
{date} {month} {year}"""

st.sidebar.write(text)
st.sidebar.divider()
status = st.sidebar.radio("Choose an operation:", options, key="Options")

if status == options[0]:
    st.subheader(":blue[Purpose:]")

    st.write("""The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
    this reduces the responsibilities of the teacher and gives them more room to breathe before classes began.""")

    st.subheader(":blue[Working:]")

    st.markdown("""
    - Images are collected on which classification is done, the collection is through streamlit's `camera_input()`.
    - Some preprocessing is done before classification to improve accuracy.
    - Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade.
    - The classification model to recognise the identity of students is a CNN model. It uses `adam` as the optimizer, `sparse_binary_crossentropy` for loss and has total ... parameters.
    - Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Panda's DataFrames.
    """)

    st.subheader(":blue[Made by:]")
    
    st.write("""
    - Arush (Data Expert)
    - Aryan Vishwakarma (Video Producer)
    - Jaffar (Information Researcher)
    - Krishna V. Gupta (Communication Leader)
    - Yusuf Zaheer (Main Coder)
    - Zoheb Arsh (Web Designer)
    """)

    st.subheader(":blue[Video:]")
    st.video(base + "our_video.mov")

    st.subheader(":blue[Resources:]")
    st.write("""
    - [Deep Learning Course by FreeCodeCamp](https://youtu.be/IA3WxTTPXqQ)
    - [OpenCV course by FreeCodeCamp](https://youtu.be/oXlwWbU8l2o)
    - [Deep Learning Course by Kaggle](https://www.kaggle.com/learn/intro-to-machine-learning)
    - [Streamlit course by RyanAndMattDataScience](https://youtu.be/eAgONwZ_dKM)
    - And many more sources were used.
    - The support of our teachers, friends and families were also vital to the success of this project.

    """)

elif status == options[1]: #mark attendance
    img = st.camera_input("Take a photo: ")

    if img:
        st.success("Capture successful!")
        with open(base + "Dataset/Predict/1.jpg", "wb") as f:
            f.write(img.getbuffer())

        fr.mark_attendance("model2")
            
elif status == options[2]: #view attendance register for a specific date or month
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Select a month:", MONTHS, index=None)
    
    with col2:
        year = st.selectbox("Select a year:", YEARS, index=None)

    if month and year:
        view_attendance(month, year)
            
elif status == options[3]: #view attendance total and percentage            
    percentage()

elif status == options[4]:
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Select a month:", MONTHS, index=None)

    with col2:
        year = st.selectbox("Select a year:", YEARS, index=None)

    if month and year:
        try:
            register = pd.read_csv(base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv")
            editable_df = st.data_editor(register)

            if st.button("**Make Changes?**"):
                editable_df.to_csv(base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv", index=False)
                st.success("Register changed!")

        except FileNotFoundError:
            st.error(f"No records available for {month} {year}")
                
elif status == options[5]: #register a student
    name = st.text_input("Enter student name:", key="Input03")
    name = name.strip().title()

    roll = st.slider("Enter roll number:", min_value=1, max_value=38, step=1, key="Input04")


    if name and roll:
        register_student(name, roll)

elif status == options[6]: #remove a student
    names = pd.read_csv(sample_path)

    names_list, options = [], []
    for idx, name in enumerate(list(names["name"])):
        names_list.append(name)
        options.append(f"{idx+1}. {name}")

    name = st.selectbox("Select a student:", options)                
    index_remove = options.index(name)

    if st.button(":red[**DELETE**]"):
        remove_student(index_remove)



            
