import face_recognition as fr
person = "Scarlett"
folder = "Scarlett Johansson"
fr.camera_capture(folder, f"/workspaces/attendance-system/attendance_system/{person}.mp4")