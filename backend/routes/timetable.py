from flask import Blueprint, jsonify, request
from backend.db.connection import get_db_connection
from auth.decorators import token_req
tt_bp = Blueprint("tt", __name__)
@tt_bp.route("/timetable", methods = ["POST"])
@token_req
def set_timetable(id):
 data = request.get_json()
 sub_id = data.get("sub_id")
 day = data.get("day")
 period_no = data.get("period_no")
 #sql query
 con = get_db_connection()
 cur = con.cursor()
 cur.execute('''
  insert into timetable(stud_id, day, period_no, sub_id) 
  select %s, %s, %s, sub_id
  from studies 
  where stud_id = %s and sub_id = %s''', 
  (id, day, period_no, id, sub_id)
  )

 if cur.rowcount == 0:
    con.rollback()
    cur.close()
    con.close()
    return jsonify({
        "error": "Please add this subject first, then try again"
    }), 404
 con.commit()
 cur.close()
 con.close()
 return "timetable created successfully", 200


@tt_bp.route("/timetable", methods = ["GET"])
@token_req
def fetch_tt(id):
 #sql query
 con = get_db_connection()
 cur = con.cursor()
 #data gives a full list so
 cur.execute('''
   select timetable.sub_id,
   subject.sub_name,
   timetable.day,
   timetable.period_no
   from timetable
   join subject 
   on timetable.sub_id = subject.sub_id
   where stud_id = %s''', 
   (id,)
  )
 if cur.rowcount == 0:
    con.rollback()
    cur.close()
    con.close()
    return jsonify({"error": "subject not found for this student"}), 404
 rec = cur.fetchall()
 cur.close()
 con.close()
 timetable = []
 for sub in rec: #fetchall() sending like [(), ()....] where each tuple represents one row and all is enclosed inside a list
   sub_id = sub[0]
   sub_name = sub[1]
   day = sub[2]
   period_no = sub[3]
   timetable.append(
     {
       "sub_id" : sub_id,
        "sub_name" : sub_name,
        "day" : day,
        "period_no" : period_no
      }
   )

 return jsonify({"subjects" : timetable}), 200


@tt_bp.route("/timetable", methods = ["PATCH"])
@token_req
def patch_tt(id):
  data = request.get_json()
  new_sub_id = data.get("new_sub_id")
  day = data.get("day")
  period_no = data.get("period_no")
  con = get_db_connection()
  cur = con.cursor()
  cur.execute('''
    update timetable 
    set sub_id = %s
    where stud_id = %s 
    and day = %s
    and period_no = %s''', 
    (new_sub_id, id, day, period_no)
  )
  if cur.rowcount == 0:
    con.rollback()
    cur.close()
    con.close()
    return jsonify({"error" : "note not found"}), 404

  con.commit()
  cur.close()
  con.close() 
  return "note updated successfully", 200


@tt_bp.route("/timetable", methods=["DELETE"])
@token_req
def delete_tt(id):

  data = request.get_json()
  day = data.get("day", "")
  period_no = data.get("period_no", "")

  # postgres
  con = get_db_connection()
  cur = con.cursor()

  cur.execute('''
  DELETE FROM timetable
  WHERE stud_id = %s
  AND day = %s
  AND period_no = %s''',
  (id, day, period_no)
  )

  if cur.rowcount == 0:
    con.rollback()
    cur.close()
    con.close()
    return jsonify({"error": "timetable entry not found"}), 404

  con.commit()
  cur.close()
  con.close()

  return jsonify({"message": "timetable entry deleted successfully"}), 200