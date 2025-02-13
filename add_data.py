# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
#
#
# cred = credentials.Certificate('C:/Users/Dwarkadhish Kamthane/Desktop/Machiene Learning/Real-time face recognition and attendance system/serviceKey.json')
# firebase_admin.initialize_app(cred ,{
#     'databaseURL':"https://face-attendance-eb515-default-rtdb.firebaseio.com/"
# })
#
# ref = db.reference('Students')
# data = {
#     "12306696":
#         {
#             "name": "Dwarkadhish D Kamthane",
#             "major": "AIML",
#             "starting year": 2023,
#             "total attendance":122,
#             "grade": "O",
#             "year" :2,
#             "last_attendance": "2025-01-14 00:30:42"
#         },
#     "12306414":
#         {
#             "name": "Kumar Ayush",
#             "major": "Data Scientist",
#             "starting year": 2023,
#             "total attendance":56,
#             "grade": "A+",
#             "year" :2,
#             "last_attendance": "2025-02-04 17:20:36 "
#         },
#
#
# }
#
# for key,value in data.items():
#     ref.child(key).set(value)

from supabase import create_client, Client

SUPABASE_URL = "https://xccejnrpvhnqbzpjymvz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhjY2VqbnJwdmhucWJ6cGp5bXZ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODYzMTcyNSwiZXhwIjoyMDU0MjA3NzI1fQ.KFj9OJ13Ax5rTC-nE6RcxL4eAjdQEpiL5bBgZeOAQZ4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

data = [
    {
        "student_id": "12306696",
        "name": "Dwarkadhish D Kamthane",
        "major": "AIML",
        "starting_year": 2023,
        "total_attendance": 86,
        "grade": "O",
        "year": 2,
        "last_attendance": "2025-01-14 00:30:42"
    },
    {
        "student_id": "12306414",
        "name": "Kumar Ayush",
        "major": "Data Scientist",
        "starting_year": 2023,
        "total_attendance": 57,
        "grade": "A+",
        "year": 2,
        "last_attendance": "2025-02-04 17:20:36"
    },
    {
        "student_id": "12306132",
        "name": "Vihan Anand",
        "major": "Full stack web developer",
        "starting_year": 2023,
        "total_attendance": 88,
        "grade": "A+",
        "year": 2,
        "last_attendance": "2025-02-07 15:10:16"
    }

]

response = supabase.table("Students").upsert(data).execute()

# Print response to verify
print(response)
