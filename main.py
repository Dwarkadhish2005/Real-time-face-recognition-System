
import os
import numpy as np
import pickle
import cv2
import face_recognition
import cvzone
from boltons.timeutils import total_seconds
from supabase import create_client, Client
from datetime import datetime


# Supabase credentials
SUPABASE_URL = "https://xccejnrpvhnqbzpjymvz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhjY2VqbnJwdmhucWJ6cGp5bXZ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODYzMTcyNSwiZXhwIjoyMDU0MjA3NzI1fQ.KFj9OJ13Ax5rTC-nE6RcxL4eAjdQEpiL5bBgZeOAQZ4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('resources/background.jpg')

folderModePath = 'resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

print("Loading Encoded File....")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encoded file loaded")

modeType = 0
counter = 0
id = -1
studentInfo = {}  # To store student data safely
imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)  # Placeholder image

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image from webcam")
        continue

    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgModeResized = cv2.resize(imgModeList[modeType], (550, 550))
    imgBackground[115:115 + 550, 808:808 + 550] = imgModeResized
    
    for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if len(faceDis) > 0:
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                id = studentIds[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 1

    if counter != 0:
        if counter == 1:
            response = supabase.table("Students").select("*").eq("student_id", id).execute()

            if response.data:
                studentInfo = response.data[0]
                print("Student Info:", studentInfo)
            else:
                print(f"No data found for Student ID: {id}")
                studentInfo = {"total_attendance": 0}

            path = f"student_images/{id}.jpg"  # Correct path
            print(f"Attempting to download: {path}")  # Debugging print

            for ext in ["jpg", "png", "jpeg"]:
                try:
                    path = f"student_images/{id}.{ext}"
                    print(f"Trying to download: {path}")  # Debugging

                    image_data = supabase.storage.from_("students_bucket").download(path)
                    if image_data:
                        array = np.frombuffer(image_data, np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                        imgStudent = cv2.resize(imgStudent, (250, 216))  # ✅ Resize Fix
                        print(f"Loaded image: {path}")
                        break  # Stop once we successfully load an image
                except Exception as e:
                    print(f"Error downloading {path}: {e}")
                    continue  # Try the next extension

            datetimeObject = datetime.strptime(studentInfo['last_attendance'],
                                              "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed>=40:
                if "total_attendance" in studentInfo:
                    studentInfo["total_attendance"] += 1
                    update_response = (
                        supabase.table("Students")
                        .update({"total_attendance": studentInfo["total_attendance"]})
                        .eq("student_id", id)
                        .execute()
                    )

                    if update_response.data:
                        print(f"Updated attendance for {id}: {studentInfo['total_attendance']}")
                    else:
                        print("Failed to update attendance")
                update_response = (
                    supabase.table("Students")
                    .update({"last_attendance": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    .eq("student_id", id)
                    .execute()
                )

                if update_response.data:
                    print(f"Updated last attendance for {id}")
                else:
                    print("Failed to update last attendance")
            else:
                modeType = 3
                counter =0
                imgModeResized = cv2.resize(imgModeList[modeType], (550, 550))
                imgBackground[115:115 + 550, 808:808 + 550] = imgModeResized
        if modeType != 3:

            if 10<counter<20:
                modeType = 2
                imgModeResized = cv2.resize(imgModeList[modeType], (550, 550))
                imgBackground[115:115 + 550, 808:808 + 550] = imgModeResized

            if counter<=10:
                cv2.putText(imgBackground, str(studentInfo.get('total_attendance', 0)), (880, 140),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo.get('name', 'N/A')), (980, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, "Major: " + str(studentInfo.get('major', 'N/A')), (980, 525),
                            cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo.get('student_id', 'N/A')), (980, 400),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, "Grade: " + str(studentInfo.get('grade', 'N/A')), (980, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(imgBackground, "Year: " + str(studentInfo.get('year', 'N/A')), (980, 570),
                            cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)

                imgBackground[160:160+216, 959:959+250] = imgStudent

            counter += 1

            if counter>=20:
                modeType=0
                counter =0
                studentInfo = []
                imgStudent = []

                imgModeResized = cv2.resize(imgModeList[modeType], (550, 550))
                imgBackground[115:115 + 550, 808:808 + 550] = imgModeResized

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
