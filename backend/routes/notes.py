from flask import Blueprint, jsonify, request
from backend.db.connection import get_db_connection
from auth.decorators import token_req
notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/notes", methods = ["POST"])
@token_req
def add_notes(id):
 stud_id = 1
 data = request.get_json()
 text = data.get("text", "")
 date = data.get("date", "")

 #sql query
 con = get_db_connection()
 cur = con.cursor()
 cur.execute('''
  insert into notes(
   stud_id,
   date,
   text
  ) 
  values(%s, %s, %s)''', 
  (id, date, text)
) #one element tuple, we use tuples to pass values here
 con.commit()
 cur.close()
 con.close()
 return "note added successfully", 200


@notes_bp.route("/notes", methods = ["GET"])
@token_req
def fetch_notes(id):
 
 date = request.args.get("date")
 #sql query
 con = get_db_connection()
 cur = con.cursor()

 #data gives a full list so
 cur.execute('''
 select text
 from notes 
 where stud_id = %s 
 and date = %s''', 
 (id, date)
 )
 rec = cur.fetchone()
 if rec is None:
  cur.close()
  con.close()
  return jsonify({"error" : "note not found"}), 404
 text = rec[0]
 cur.close()
 con.close()
 return jsonify({"text" : text}), 200



@notes_bp.route("/notes", methods = ["PATCH"])
@token_req
def edit_note(id):
  
  data = request.get_json()
  date = data.get("date", "")
  new_note = data.get("new_note")

 #sql query
  con = get_db_connection()
  cur = con.cursor()
  cur.execute('''
  update notes 
  set text = %s 
  where stud_id = %s 
  and date = %s''',
  (new_note, id, date)
  ) #one element tuple, we use tuples to pass values here
  if cur.rowcount == 0:
   con.rollback()
   cur.close()
   con.close()
   return jsonify({"error" : "note not found"}), 404

  con.commit()
  cur.close()
  con.close() 
  return "note updated successfully", 200
  

@notes_bp.route("/notes", methods = ["DELETE"])
@token_req
def del_note(id):
  
  data = request.get_json()
  date = data.get("date")

  #sql query
  con = get_db_connection()
  cur = con.cursor() 
  cur.execute('''
  delete from notes
  where stud_id = %s
  and date = %s''',
  (id, date)
  )
  if cur.rowcount == 0:
   con.rollback()
   cur.close()
   con.close()
   return jsonify({"error" : "note not found"}), 404
  con.commit()
  cur.close()
  con.close()
  return "note deleted successfully", 200
