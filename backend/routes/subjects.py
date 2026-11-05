
from flask import Blueprint as bp
from flask import request, jsonify
from backend.db.connection import get_db_connection
from auth.decorators import token_req
sub_bp = bp("subjects", __name__)
@sub_bp.route("/subjects", methods = ["GET"])
@token_req
def fetch_sub(id):
   
 #sql query
   con = get_db_connection()
   cur = con.cursor()
 #data gives a full list so
   cur.execute('''
   select subject.sub_id, subject.sub_name 
   from subject join studies on subject.sub_id = studies.sub_id 
   where studies.stud_id = %s''', 
   (id,)
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

   return jsonify({"subjects" : subnames}), 200



@sub_bp.route("/subjects", methods = ["POST"])
@token_req
def add_sub(id):
  data = request.get_json()
  subjects = data.get("subject", [])
  sub_name = data.get("sub_name", [])
  #sql query
  con = get_db_connection()
  cur = con.cursor()
  #data gives a full list so
  for sub in subjects:
    cur.execute('''
        insert into subject(sub_name)
        values(%s)
        returning sub_id''', 
        (sub,)
      ) #one element tuple, we use tuples to pass values here
    sub_id = cur.fetchone()[0]
    cur.execute("""
      insert into studies (stud_id, sub_id, subject_name)
      values (%s, %s, %s)
      """, 
      (id, sub_id, sub_name))
  
  con.commit()
  cur.close()
  con.close()
  return "subjects added successfully", 200


 
@sub_bp.route("/subjects", methods = ["PATCH"])
@token_req
def edit_sub(id):
  data = request.get_json()
  sub_id = data.get("sub_id")
  new_sub_name = data.get("new_sub_name")

 #sql query
  con = get_db_connection()
  cur = con.cursor()
  #data gives a full list so
 
  cur.execute('''
  UPDATE studies
  SET subject_name = %s
  WHERE sub_id = %s
  AND stud_id = %s;''',
  (new_sub_name, sub_id, id)
  ) #one element tuple, we use tuples to pass values here
  con.commit()
  cur.close()
  con.close()
  return "subject updated successfully", 200

@sub_bp.route("/subjects", methods = ["DELETE"])
@token_req
def del_sub(id):
   
   data = request.get_json()
   sub_id = data.get("sub_id")

   #sql query
   con = get_db_connection()
   cur = con.cursor()
   #data gives a full list so
   cur.execute('''
   delete from studies
   where sub_id = %s 
   and stud_id = %s''',
   (sub_id, id)
   )
   con.commit()
   cur.close()
   con.close()
   return "subject deleted successfully", 200
