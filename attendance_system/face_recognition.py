import streamlit as st
import random as rn
import pandas as pd
import numpy as np
import pathlib as pt
import pickle
import cv2
import time

def read_img(img):
    import tensorflow as tf

    filepath = "/mount/src/attendance-system/attendance_system/predict.jpg"
    with open(filepath, "wb") as f:
        f.write(img.getbuffer())

    img = tf.keras.utils.load_img(filepath, target_size=(128, 128))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    return img_array


def camera_capture(folder, camera_index=0):        
    capture = cv2.VideoCapture(camera_index)
    count = 0

    haar_cascade = cv2.CascadeClassifier("/mount/src/attendance-system/attendance_system/haarcascade_frontalface_default.xml")

    while True:
        success, frame = capture.read()
        count += 1

        if not success:
            st.write("Could not read from camera")
            break
    
        #there many be multiple faces detected, we will only keep one (at index 0)
        #haar cascade gives four points, which when connected, form a rectangle enclosing the face

        #blurred = cv2.GaussianBlur(frame, (1,1), cv2.BORDER_DEFAULT)
        #grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        #frame = cv2.equalizeHist(frame)

        faces_detected = haar_cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=5)

        if len(faces_detected) != 0:
            face_rectangle = faces_detected[0]
            x, y, w, h = face_rectangle
            cropped = frame[y:y+h, x:x+w]

            if count%9 == 0:
                height, width = cropped.shape[:2]
                angle = rn.randint(35, 50)
                angle = rn.choice([1, -1]) * angle
                rotation_matrix = cv2.getRotationMatrix2D((width/2,height/2), angle, 1)
                cropped = cv2.warpAffine(cropped, rotation_matrix, (width, height))

            print("Progress: ", count)

            if count%3 == 0:
                cv2.imwrite(f"/mount/src/attendance-system/attendance_system/Dataset/Train/{folder}/{count}.jpg", cropped)

            elif count%5 == 0:
                cv2.imwrite(f"/mount/src/attendance-system/attendance_system/Dataset/Test/{folder}/{count}.jpg", cropped)

    capture.release()
    #cv2.destroyAllWindows()

def mark_attendance(img, model):
    import tensorflow as tf

    date, month, year = time.strftime("%d %B %Y").split()
    
    path = pt.Path(f"/mount/src/attendance-system/attendance_system/attendance_dataset/attendance_{year}")

    try:
        register = pd.read_csv(path / f"attendance_{month}.csv")

    except FileNotFoundError:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

            with open("/mount/src/attendance-system/attendance_system/years.dat", "rb+") as f:
                years = pickle.load(f)
                years.append(year)
                pickle.dump(years, f)

        register = pd.read_csv("/mount/src/attendance-system/attendance_system/sample_register.csv")
  
    if not date in register.columns:
        register.loc[:, date] = "A"


    model = tf.keras.models.load_model(f"/mount/src/attendance-system/attendance_system/{model}.keras")

    img_array = read_img(img)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    classes = list(register["name"])
    student = classes[np.argmax(score)]

    print("Predicted Student:", student)
    print(f"Confidence: {100*np.max(score):.2f}%")

    student_rolls = list(register.index)
    idx = student_rolls[np.argmax(score)] 

    register.loc[idx, date] = "P"            
    register.to_csv(path / f"attendance_{month}.csv", index=False)

    st.dataframe(register)
    