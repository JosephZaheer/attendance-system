import streamlit as st
import pathlib as pt
import pandas as pd
import cv2
import csv

toolpath = pt.Path("/workspaces/attendance-system/tools")
dbpath = toolpath / "train_test_dataset"
metapath = toolpath / "metadata.csv"

################################################################################

def camera_capture(name, camera_index):        
    capture = cv2.VideoCapture(camera_index)
    count = 0
    haar_cascade = cv2.CascadeClassifier(toolpath / "haarcascade_frontalface_default.xml")

    while True:
        success, frame = capture.read()
        count += 1

        if not success:
            st.write("Could not read from camera")
            break

        #there many be multiple faces detected, we will only keep one (at index 0)
        faces_detected = haar_cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=5)

        if len(faces_detected) != 0:
            #haar cascade gives four points, which when connected, form a rectangle enclosing the face
            face_rectangle = faces_detected[0]
            x, y, w, h = face_rectangle
            cropped = frame[y:y+h, x:x+w]

            #blurred = cv2.GaussianBlur(cropped, (1,1), cv2.BORDER_DEFAULT)
            grey = cv2.cvtColor(grey, cv2.COLOR_BGR2GRAY)
            equal = cv2.equalizeHist(grey)
            
            if count%3 == 0:
                cv2.imwrite(dbpath / f"train/{name}/{count}.jpg", equal)

            elif count%5 == 0:
                print("Progress: ", count)
                cv2.imwrite(dbpath / f"test/{name}/{count}.jpg", equal)
            
    capture.release()
    #cv2.destroyAllWindows()
    
################################################################################

def upload_video(name, count):
    video = st.file_uploader("Upload a video (indoors): ", type=["mp4", "mov", "webm"], key=f"{count}file_upload")

    if video:
        with open(toolpath / f"current_collection_target.mp4", "wb") as f:
            f.write(video.getbuffer())
    
        camera_capture(name, toolpath / f"current_collection_target.mp4")
        
################################################################################

def register(name, roll):
    #check if name is valid
    if not name.replace(" ", "").isalpha():
            st.error("Name must not contain numbers (1, 2, 3, ...) or special characters (#, &, @, $, ...)")
            return None

    register = pd.read_csv(metapath)
    names = tuple(register["name"])

    #roll = index + 1
    if roll in register["roll"] and name == names[roll - 1]:
        st.error("Student already registered!")
        return None

    records = []
    for i in range(len(names)):
        _roll = int(register.iloc[i, 0])
        _name = register.iloc[i, 1]
        records.append((_roll, _name))

    #records = [(roll, name), (roll, name), (roll, name), ...]
    #by sorting, all records are arranged sequentially according to the roll numbers
    records.append((int(roll), name))
    records.sort()

    path = dbpath / "train" / name
    if not path.exists():
        path.mkdir(parents=True)
        
    path = dbpath / "test" / name
    if not path.exists():
        path.mkdir(parents=True)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        upload_video(name, 1) #indoors, against a wall

    with col2:
        upload_video(name, 2) #indoors, against a different wall

    with col3:
        upload_video(name, 3) #outside, with sky in background

    if st.button("**Register**"):
        st.divider()

        with open(metapath, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
            writer.writerows(records)

        st.success("Registration Successful!")

        show = pd.read_csv(metapath)
        st.table(show)

################################################################################
    
name = st.text_input("Enter student name:", key="Input03")
name = name.strip().title()

roll = st.slider("Enter roll number:", min_value=1, max_value=38, step=1, key="Input04")

if name and roll:
    register(name, roll)
    
