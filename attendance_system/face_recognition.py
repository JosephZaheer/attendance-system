import streamlit as st
import random as rn
import pandas as pd
import numpy as np
import time
import cv2
import os

#base = "/mount/src/attendance-system/attendance_system/"
base = "/workspaces/attendance-system/attendance_system/"

IMG_SIZE = 224

def camera_capture(name, camera_index=0):        
    capture = cv2.VideoCapture(camera_index)
    count = 0

    haar_cascade = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")

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

            if rn.random() < 0.2:
                height, width = cropped.shape[:2]
                angle = rn.randint(35, 50) * rn.choice([1, -1])
                rotation_matrix = cv2.getRotationMatrix2D((width/2,height/2), angle, 1)
                cropped = cv2.warpAffine(cropped, rotation_matrix, (width, height))

            blurred = cv2.GaussianBlur(cropped, (1,1), cv2.BORDER_DEFAULT)
            grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
            equal = cv2.equalizeHist(grey)
            
            print("Progress: ", count)

            if count%3 == 0:
                cv2.imwrite(base + f"Dataset/Train/{name}/{count}.jpg", grey)

            elif count%5 == 0:
                cv2.imwrite(base + f"Dataset/Test/{name}/{count}.jpg", grey)

    capture.release()
    #cv2.destroyAllWindows()

def mark_attendance(model):
    import tensorflow as tf

    date, month, year = time.strftime("%d %B %Y").split()

    try:
        register = pd.read_csv(base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv")

    except FileNotFoundError:
        if not os.path.exists(base + f"attendance_dataset/attendance_{year}"):
            os.mkdir(base + f"attendance_dataset/attendance_{year}")

        register = pd.read_csv(base + "sample_register.csv")
  
    if not date in register.columns:
        register.loc[:, date] = "A"

    img_path = base + "Dataset/Predict/1.jpg"
    model = tf.keras.models.load_model(base + f"{model}.keras")
    img = tf.keras.utils.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    """
    img = tf.keras.utils.image_dataset_from_directory(
    base + "Dataset/Predict",
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=1
    )"""

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    classes = list(register["name"])
    student = classes[np.argmax(score)]

    print("\n", "#"*50, "\n", "#"*50, "\n")
    print("Predicted Student:", student)
    print(f"Confidence: {100*np.max(score):.2f}%")
    print("\n", "#"*50, "\n", "#"*50, "\n")

    student_rolls = list(register.index)
    idx = student_rolls[np.argmax(score)] 

    register.loc[idx, date] = "P"            
    register.to_csv(base + f"attendance_dataset/attendance_{year}/attendance_{month}.csv", index=False)

    st.table(register)
    