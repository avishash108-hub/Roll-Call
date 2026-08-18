from os import name

from flask import Flask, jsonify, request
import requests
import psycopg
app = Flask(__name__)
@app.route('/')
def home():
    return "my flask is running"

@app.route("/subjects", methods = ["GET"])

def fetch_sub():
   stud_id = 1
 #sql query
   con = psycopg.connect(
      dbname = "att",
      user = "postgres",
      password = "avi",
      host = "localhost",
      port = "5432"
    )
   cur = con.cursor()
 #data gives a full list so
   cur.execute('''
   select subject.sub_id, subject.sub_name 
   from subject join studies on subject.sub_id = studies.sub_id 
   where studies.stud_id = %s''', 
   (stud_id,)
   )
   rec = cur.fetchall()
   cur.close()
   con.close()
   subnames = []
   for sub in rec: #fetchall() sending like [(), ()....] where each tuple represents one row and all is enclosed inside a list
     sub_id = sub[0]
     sub_name = sub[1]
     subnames.append(
      {
         "sub_id" : sub_id,
         "sub_name" : sub_name
      }
    ) 

   return jsonify({"hello" : "subjects working"}), 200


@app.route("/subjects", methods = ["POST"])
 #stud_id = from jwt
def add_sub():
  data = request.get_json()
  subjects = data.get("subject", "")
  #sql query
  con = psycopg.connect(
      dbname = "att",
      user = "postgres",
      password = "avi",
      host = "localhost",
      port = "5432"
 )
  cur = con.cursor()
  #data gives a full list so
  for sub in subjects:
     cur.execute('''
     insert into subject(sub_name)
     values(%s)''', 
     (sub, )
  ) #one element tuple, we use tuples to pass values here
  con.commit()
  cur.close()
  con.close()
  return "subjects added successfully", 200
 
@app.route("/subjects", methods = ["PATCH"])
#stud_id = from jwt
def edit_sub():
  stud_id = 1
  data = request.get_json()
  sub_id = data.get("sub_id")
  new_sub_name = data.get("new_sub_name")

 #sql query
  con = psycopg.connect(
        dbname = "att",
        user = "postgres",
        password = "avi",
        host = "localhost",
        port = "5432"
      )
  cur = con.cursor()
  #data gives a full list so
 
  cur.execute('''
  update subject
  set sub_name = %s
  where sub_id = %s 
  and sub_id in 
  (select sub_id 
  from studies 
  where stud_id = %s)''',
  (new_sub_name, sub_id, stud_id)
  ) #one element tuple, we use tuples to pass values here
  con.commit()
  cur.close()
  con.close()
  return "subject updated successfully", 200

@app.route("/subjects", methods = ["DELETE"])
#stud_id = from jwt
def del_sub():
   stud_id = 1
   data = request.get_json()
   sub_id = data.get("sub_id")

   #sql query
   con = psycopg.connect(
      dbname = "att",
      user = "postgres",
      password = "avi",
      host = "localhost",
      port = "5432"
   )
   cur = con.cursor()
   #data gives a full list so
   cur.execute('''
   delete from subject 
   where sub_id = %s 
   and sub_id in
   (select sub_id 
   from studies
   where stud_id = %s)''',
   (sub_id, stud_id)
   )
   con.commit()
   cur.close()
   con.close()
   return "subject deleted successfully", 200




if __name__ == '__main__':
    app.run(debug=True)