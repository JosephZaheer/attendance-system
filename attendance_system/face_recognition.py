import tensorflow as tf
import streamlit as st
import pandas as pd
import numpy as np
import time

#import cv2

def read_img(img):

    st.write("hello")
    filepath = "/workspaces/attendance-system/attendance_system/test.jpg"

    with open(filepath, "wb") as f:
        f.write(img.getbuffer(), f)

    img = tf.keras.utils.load_img(filepath, target_size=(128, 128))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    return img_array

"""
def streamlit_camera():
    picture = st.camera_input("Take a photo")

    if picture is not None:
        bytes_data = picture.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        return cv2_img
        #cv2.imwrite("attendance_system/picture.png", cv2_img)
    
    return None


def camera_capture(camera_index=0, max_frames=300):        
    capture = cv2.VideoCapture(camera_index)
    count = 0
        
    while True:
        success, frame = capture.read()
        count += 1

        if not success:
            st.write("Could not read from camera")
            break
                
        if count >= max_frames:
            break

        yield frame      

    capture.release()
    try:
        cv2.destroyAllWindows()
    except:
        pass

def preprocessing(image):
    #there many be multiple faces detected, we will only keep one (at index 0)
    #haar cascade gives four points, which when connected, form a rectangle enclosing the face

    haar_cascade = cv2.CascadeClassifier("attendance_system/haarcascade_frontalface_default.xml")

    blurred = cv2.GaussianBlur(image, (1,1), cv2.BORDER_DEFAULT)
    grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    faces_detected = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=10)

    if len(faces_detected) != 0:
        face_rectangle = faces_detected[0]
        x, y, w, h = face_rectangle
        cropped = grey[y:y+h, x:x+w]

        return cropped

    return None

def add_to_dataset(name, image, idx=0):
    cv2.imwrite(f"attendance_system/Dataset/{name}/train/Image{idx}.webp", image)
"""

def mark_attendance(img):
    date, month, year = time.strftime("%d %B %Y").split()
    
    if len(date) == 1:
        date = "0" + date

    filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"

    try:
        register = pd.read_csv(filepath)

    except FileNotFoundError:
        register = pd.read_csv("attendance_system/sample_register.csv")
    
    if not date in register.columns:
        register.loc[:, date] = "A"

    model = tf.keras.models.load_model("/workspaces/attendance-system/attendance_system/model1.keras")

    img_array = read_img(img)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    print(f"{predictions=}")
    print(f"{score=}")

    #classes = list(register["name"])
    classes = ["Aryan", "Jaffar", "Zoheb"]
    student = classes[np.argmax(score)]

    print("Predicted Student:", student)
    print(f"Confidence: {100*np.max(score):.2f}%")

    student_rolls = [1, 3, 6]
    idx = student_rolls[np.argmax(score)] - 1

    register.loc[idx, date] = "P"            
    register.to_csv(filepath, index=False)

    st.dataframe(register)
    
