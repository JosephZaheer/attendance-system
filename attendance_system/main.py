import face_recognition as fr
import streamlit as st
import pandas as pd
import time
import csv
import os
           
#_______________USEFUL FUNCTIONS_______________

def show_deleted(register):
    full_names = tuple(pd.read_csv(sample_path)["name"])

    if len(full_names) != register.shape[0]:
        if not st.checkbox("Show Deleted Student?"):

            truth = []
            for idx in register.index:
                truth.append(register.loc[idx, "name"] in full_names)

            cleaned = register[truth]
            cleaned["roll"] = range(1, sum(truth) + 1)
            return cleaned
    
    return register

def view_attendance(month, year):
    try:
        register = pd.read_csv(base + f"records/{year}/{month}.csv")
         
    except FileNotFoundError:
        st.error(f"No records available for {month} {year}")
        return None

    date = st.slider("Specify a date:", min_value=0, max_value=31, step=1)
    st.caption("Select 0 for whole month")

    if date == 0: #whole month
        columns = list(register.columns)
        
    else: #one specific date
        if str(date) in register.columns:
            columns = ["roll", "name", str(date)]
            
        else:
            st.error(f"Attendance not availabe for this date: {date}")
            return None

    show = show_deleted(register[columns])
    show = show.set_index(show["roll"]).drop("roll", axis=1)
    st.dataframe(show)

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

    percent = pd.read_csv(sample_path)
    percent["Total"] = ""
    working_days = 0
                
    for month in months:
        filepath = base + f"records/{year}/{month}.csv"
                    
        try:
            register = pd.read_csv(filepath)
                        
        except FileNotFoundError:
            continue

        #attendance_register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            percent["Total"] += 1 if register[column] == "P" else 0

    if working_days == 0:
        st.error("No attendance for the given month(s).")
        return None

    for idx, row in enumerate(percent["Total"]):
        percent.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"

    st.caption(f"Working days: {working_days}")
    show = percent.set_index(percent["roll"]).drop("roll", axis=1)
    show = show_deleted(show)
    st.dataframe(show)
    
def make_changes(month, year):
    try:
        register = pd.read_csv(base + f"records/{year}/{month}.csv")
        register = show_deleted(register)
        editable_df = st.data_editor(register)

        if st.button("**Make Changes?**"):
            editable_df.to_csv(base + f"records/{year}/{month}.csv", index=False)
            st.success("Register changed!")

    except FileNotFoundError:
        st.error(f"No records available for {month} {year}")

def upload_video(NAME, count):
    video = st.file_uploader("Upload a video (indoors): ", type=["mp4", "mov"], key=f"{count}file_upload")

    if video:
        with open(base + f"Dataset/Videos/{NAME}1.mp4", "wb") as f:
            f.write(video.getbuffer())
    
        fr.camera_capture(NAME, base + f"/Dataset/Videos/{NAME}{count}.mp4")

def register_student(NAME, ROLL):
    #check if name is valid
    if not NAME.replace(" ", "").isalpha():
            st.error("Name must not contain numbers (1, 2, 3, ...) or special characters (#, &, @, $, ...)")
            return None

    register = pd.read_csv(sample_path)
    names = tuple(register["name"])

    #roll = index + 1
    if ROLL in register["roll"] and NAME == names[ROLL - 1]:
        st.error("Student already registered!")
        return None

    records = []
    for i in range(len(names)):
        roll = int(register.iloc[i, 0])
        name = register.iloc[i, 1]
        records.append((roll, name))

    #records = [(roll, name), (roll, name), (roll, name), ...]
    #by sorting, all records are arranged sequentially according to the roll numbers
    records.append((int(ROLL), NAME))
    records.sort()

    if not os.path.exists(base + f"Dataset/Train/{NAME}"):
        os.mkdir(base + f"Dataset/Train/{NAME}")

    if not os.path.exists(base + f"Dataset/Test/{NAME}"):
        os.mkdir(base + f"Dataset/Test/{NAME}")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        upload_video(NAME, 1) #indoors, against a wall

    with col2:
        upload_video(NAME, 2) #indoors, against a different wall

    with col3:
        upload_video(NAME, 3) #outside, with sky in background

    if st.button("**Register**"):
        st.divider()

        with open(sample_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
            writer.writerows(records)

        st.success("Registration Successful!")

        show = pd.read_csv(sample_path)
        st.table(show)
                            
def remove_student():
    register = pd.read_csv(sample_path)

    names, options = [], []
    for idx, name in enumerate(list(register["name"])):
        names.append(name)
        options.append(f"{idx+1}. {name}")
    
    name = st.selectbox("Select a student:", options)
    try:
        index_remove = options.index(name)

    except ValueError:
        st.error("Invalid Input")
        return None

    if st.button(":red[**DELETE**]"):
        file = open(sample_path, "w")
        writer = csv.writer(file)
        writer.writerow(["roll", "name"])

        removed = False
        for idx in register.index:
            if idx == index_remove:
                removed = True
                continue
                        
            row = list(register.loc[idx])
            if removed:
                row[0] -= 1
                        
            writer.writerow(row)
        file.close()

        st.success("Deletion Successful!")

        show = pd.read_csv(sample_path)
        show = show.set_index(show["roll"]).drop("roll", axis=1)
        st.table(show)
        
def sidebar():
    day, date, month, year = time.strftime("%A %d %B %Y").split()
    
    st.sidebar.write(f"""It's **{day}**,
        {date} {month} {year}""")
        
    st.sidebar.divider()
    status = st.sidebar.radio("Choose an operation:", options)
    st.sidebar.divider()

    col1, col2 = st.columns(2)
    with col1:
        classes = []
        folders = os.listdir(base)

        for folder in folders:
            classes.append(int(folder))

        classes.sort(reverse=True)
        standard = st.sidebar.selectbox("Class", classes)
        
    with col2:
        sections = []
        folders = os.listdir(base + f"{standard}/")

        for folder in folders:
            sections.append(folder)

        section = st.sidebar.selectbox("Section", sections)
        
    if standard and section:
        return status, standard, section

#_______________STREAMLIT MENU_______________

st.title(":violet[AI ATTENDANCE SYSTEM]")
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

#base = "/mount/src/attendance-system/"
base = "/workspaces/attendance-system/database/"

status, standard, section = sidebar()

base += f"{standard}/{section}/"

sample_path = base + f"sample_register.csv"

fr.initialise(base)

YEARS = []
folders = os.listdir(base + "records")
for folder in folders:
    YEARS.append(folder)

YEARS.sort(reverse=True)
MONTHS = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]

if status == options[0]:
    st.subheader(":blue[Purpose:]")

    st.write("""The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
    this reduces the responsibilities of the teacher and gives them more room to breathe before classes began.""")

    st.subheader(":blue[Working:]")

    st.markdown("""
    - Images are collected on which classification is done, the collection is through streamlit's `file_uploader()` and `camera_input()`.
    - Some preprocessing is done before classification to improve accuracy.
    - Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade.
    - The classification model to recognise the identity of students is a CNN model. It uses `adam` as the optimizer, `sparse_binary_crossentropy` for loss and has total ... parameters.
    - Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Pandas' DataFrames.
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

    #st.subheader(":blue[Video:]")
    #st.video(base + "our_video.mov")

    st.subheader(":blue[Resources:]")
    st.write("""
    - [Deep Learning Course by FreeCodeCamp](https://youtu.be/IA3WxTTPXqQ)
    - [OpenCV course by FreeCodeCamp](https://youtu.be/oXlwWbU8l2o)
    - [Deep Learning Course by Kaggle](https://www.kaggle.com/learn/intro-to-machine-learning)
    - [Streamlit course by RyanAndMattDataScience](https://youtu.be/eAgONwZ_dKM)
    - And many more sources were used.
    - The support of our teachers, friends and families was also vital to the success of this project.
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

elif status == options[4]: #make changes to a register
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Select a month:", MONTHS, index=None)

    with col2:
        year = st.selectbox("Select a year:", YEARS, index=None)

    if month and year:
        make_changes(month, year)
                
elif status == options[5]: #register a student
    name = st.text_input("Enter student name:", key="Input03")
    name = name.strip().title()

    roll = st.slider("Enter roll number:", min_value=1, max_value=38, step=1, key="Input04")

    if name and roll:
        register_student(name, roll)

elif status == options[6]: #remove a student
    remove_student()



            
