import attendance

fr = attendance.FaceRecognition()
fr.camera_capture("attendance_system/Dataset/Aryan/Train/Aryan1.mp4", )
fr.add_to_dataset("Aryan")
