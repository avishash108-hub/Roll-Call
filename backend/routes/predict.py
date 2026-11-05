from flask import Blueprint, jsonify, request
from backend.db.connection import get_db_connection
from auth.decorators import token_req
pred_bp = Blueprint("pred", __name__)
@pred_bp.route("/predict", methods = ["GET"])
@token_req
#FRONTEND SENDS : {"sub_id" = ...}
def predict(id):
 sub_id = request.args.get('sub_id') #in query params
 #sql query
 con = get_db_connection()
 cur = con.cursor()
 cur.execute('''
 select count(*)
 from attendance 
 where stud_id = %s
 and sub_id = %s 
 and status = 'present' 
 ''', 
 (id, sub_id)
 )
 rec = cur.fetchone() #returns [(17, )] single valued tuple so we use rec[0] to fetch the count, we use fetchone because we expect only single answer to be returned
 attended_classes = rec[0] 
 cur.execute('''
 select count(*)
 from attendance 
 where stud_id = %s
 and sub_id = %s 
 and status in 
 ('present', 'absent')''', 
 (id, sub_id)
 )
 rec1 = cur.fetchone()
 total_classes = rec1[0] 
 con.commit()
 cur.close()
 con.close()

 #business logic
 try:
   att_percentage = (attended_classes / total_classes) * 100
 except ZeroDivisionError:
    return jsonify({"error" : "no classes occurred yet"}), 200
 

#for predicting safe leaved
 safe_count = 0
 total = total_classes #dont destroy original variables
 while(attended_classes / (total + 1) >= 0.75): #total is the hypothetical variable, it checks that if i dont attend one more class ie total still increases by 1 so total + 1 and attended_classes remain same as the db, so will att >= 0.75?
   total += 1
   safe_count += 1

#for recovery classes
 recovery_count = 0
 total = total_classes
 att = attended_classes
 while(att / total < 0.75):
   total_classes += 1
   recovery_count += 1
   att += 1


 return jsonify({
 "attendance percentage : " : att_percentage,
 "safe leaves : " : safe_count,
 "recovery classes : "  : recovery_count
}), 200