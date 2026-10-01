#import tensorflow as tf
import streamlit as st
import pandas as pd
import time
import cv2
import csv


class FaceRecognition:

    def __init__(self):
        pass
        #self.model = model

    def camera_capture(self, camera_index=0, max_frames=300, res=(224, 224)):
        haar_cascade = cv2.CascadeClassifier("attendance_system/haarcascade_frontalface_default.xml")
        capture = cv2.VideoCapture(camera_index)
        self.frames = []
        
        while True:
            success, frame = capture.read()

            if not success:
                st.write("Could not read from camera")
                break
                
            if len(self.frames) >= max_frames:
                break

            blurred = cv2.GaussianBlur(frame, (1,1), cv2.BORDER_DEFAULT)
            grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

            #there many be multiple faces detected, we will only keep one (at index 0)
            #haar cascade gives four points, which when connected, form a rectangle enclosing the face

            faces_detected = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=10)
            try:
                face_rectangle = faces_detected[0]
                x, y, w, h = face_rectangle
                cropped = grey[y:y+h, x:x+w]
                self.frames.append(cropped)        
            
            except Exception as e:
                st.write(e)
                pass

        capture.release()
        try: cv2.destroyAllWindows()
        except: pass

    def add_to_dataset(self, name):
        #or just train model here directly
        for idx, frame in enumerate(self.frames):
            cv2.imwrite(f"attendance_system/Dataset/{name}/train/Image{idx}.webp", frame)

    def mark_attendance(self):
        date, month, year = time.strftime("%d %B %Y").split()
        date = "0" + date

        filepath = f"attendance_system/attendance_dataset/attendance_{year}/attendance_{month}.csv"

        try:
            attendance_register = pd.read_csv(filepath)

        except FileNotFoundError:
            attendance_register = pd.read_csv("attendance_system/sample_register.csv")
    
        if not date in attendance_register.columns:
            attendance_register.loc[:, date] = "A"

        #prediction = self.model.predict(self.frames)
        #confidence = tf.nn.softmax(prediction)
        #attendance_register.loc[prediction, date] = "P"            
        #attendance_register.to_csv(filepath, index=False)
    
#Functions for general operations on attendance register
