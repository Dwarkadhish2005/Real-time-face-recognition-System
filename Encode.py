# import cv2
# import os
# import face_recognition
# import pickle
#
# import firebase_admin
# from firebase_admin import credentials
# from  firebase_admin import db
# from firebase_admin import storage
#
# cred = credentials.Cerificate("servicekey.json")
# firebase_admin.initialize_app(cred , {
# 'databaseURL':"",
# 'storageBucket':""
# })
# folderPath = 'C:/Users/Dwarkadhish Kamthane/Desktop/Machiene Learning/Real-time face recognition and attendance system/images'
# pathList = os.listdir(folderPath)
# # print(pathList)
# imgList = []
# studentIds =[]
# for path in pathList:
#     imgList.append(cv2.imread(os.path.join(folderPath,path)))
#     # print(os.path.splitext(path)[0])
#     studentIds.append(os.path.splitext(path)[0])
#
#     fileName = os.path.join(folderPath , path)
#     bucket = storage.bucket()
#     blob = bucket.blob(fileName)
#     blob.upload_from_filename(fileName)
# print(studentIds)
#
# def findEncodings(imagesList):
#     encodeList =[]
#     for img in imagesList:
#         img = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
#
#     return encodeList
# print("Encoding Started.....")
# encodeListKnown = findEncodings(imgList)
# encodeListKnownWithIds = [encodeListKnown , studentIds]
# print("Encoding Complete")
#
# file = open("EncodeFile.p",'wb')
# pickle.dump(encodeListKnownWithIds , file)
# file.close()
# print("File Saved ")

import cv2
import os
import face_recognition
import pickle
import json  # For encoding face encodings as JSON

from supabase import create_client, Client

# Supabase Credentials
SUPABASE_URL = "https://xccejnrpvhnqbzpjymvz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhjY2VqbnJwdmhucWJ6cGp5bXZ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODYzMTcyNSwiZXhwIjoyMDU0MjA3NzI1fQ.KFj9OJ13Ax5rTC-nE6RcxL4eAjdQEpiL5bBgZeOAQZ4"

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Path to images
folderPath = "C:/Users/Dwarkadhish Kamthane/Desktop/Machiene Learning/Real-time face recognition and attendance system/images"
pathList = os.listdir(folderPath)

imgList = []
studentIds = []
image_urls = []

# Upload images to Supabase Storage and store URLs
print("Uploading images to Supabase...")
for path in pathList:
    img_path = os.path.join(folderPath, path)
    imgList.append(cv2.imread(img_path))

    student_id = os.path.splitext(path)[0]
    studentIds.append(student_id)

    # Upload to Supabase Storage
    with open(img_path, "rb") as file:
        storage_path = f"student_images/{path}"  # Store in a folder
        response = supabase.storage.from_("students_bucket").upload(storage_path, file, {"content-type": "image/jpeg"})

    # Get public URL
    image_url = supabase.storage.from_("students_bucket").get_public_url(storage_path)
    image_urls.append(image_url)

print("Image Upload Completed.")
print(studentIds)


# Function to find encodings
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(img)
        if encoding:  # Ensure face encoding exists
            encodeList.append(encoding[0].tolist())  # Convert to list for JSON storage
        else:
            encodeList.append(None)  # Store as None if no face found
    return encodeList


print("Encoding Faces...")
encodeListKnown = findEncodings(imgList)
print("Encoding Complete.")

# Save encodings and student data in Supabase
# print("Saving Encodings to Database...")
# for i, student_id in enumerate(studentIds):
#     if encodeListKnown[i] is not None:  # Ensure valid encoding
#         data = {
#             "id": student_id,
#             "name": student_id.replace("_", " "),  # Placeholder name
#             "encoding": json.dumps(encodeListKnown[i]),  # Convert to JSON
#             "image_url": image_urls[i]
#         }
#         supabase.table("Students").upsert([data]).execute()
#
# print("Data successfully saved to Supabase!")

# Save encodings locally for backup
with open("EncodeFile.p", "wb") as file:
    pickle.dump([encodeListKnown, studentIds], file)

print("File Saved Locally.")
