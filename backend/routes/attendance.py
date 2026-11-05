from flask import Blueprint, jsonify, request
from backend.db.connection import get_db_connection
from auth.decorators import token_req
att_bp = Blueprint("attendance", __name__)
@att_bp.route("/attendance", methods = ["POST"])
@token_req
def add_att(id):

  data = request.get_json()
  sub_id = data.get("sub_id", "")
  date = data.get("date", "")
  status = data.get("status", "")
  period_no = data.get("period_no", "")

#postgres
  con = get_db_connection()
  cur = con.cursor()
  cur.execute('''
  insert into attendance
  (
   stud_id,
   sub_id, 
   date,
   status,
   period_no
  ) 
  values(%s, %s, %s, %s, %s)''', 
  (id, sub_id, date, status, period_no)
  ) #one element tuple, we use tuples to pass values here
  con.commit()
  cur.close()
  con.close()
  return "attendance updated successfully", 200


@att_bp.route("/attendance", methods = ["GET"])
@token_req
def fetch_att(id):
   
   date = request.args.get("date")
   
   #sql query
   con = get_db_connection()
   cur = con.cursor()
   cur.execute('''
   select attendance.date, 
   subject.sub_name,
   attendance.status, attendance.period_no
   from attendance 
   join subject on
   attendance.sub_id = subject.sub_id 
   where attendance.date = %s 
   and attendance.stud_id = %s''',
   (date, id)
  )
 #fetching recs
   records = cur.fetchall()
   cur.close()
   con.close()
   #building json
   att = []
   for row in records:
      att.append(
        {
           "date" : row[0],
           "subject" : row[1],
           "status" : row[2],
           "period" : row[3],

       }
   )
   return jsonify({"attendance" : att}), 200


