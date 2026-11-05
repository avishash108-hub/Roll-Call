from flask import Blueprint, request, jsonify
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from auth.security import secret, ph
from backend.db.connection import get_db_connection
auth_bp = Blueprint("auth", __name__)
@auth_bp.route('/register', methods = ["POST"])
def register():
  data = request.get_json()
  field = ["email", "password"]
  for i in field:
    if not data.get(i):
      return jsonify({"error" : "missing field"}), 400
  email = data.get("email")  
  username = data.get("username", "")
  password = data.get("password")
  branch =  data.get("branch", "")
  section = data.get("section", "")
  #hashing the pwd
  if(
     len(password) < 10 or len(password) > 128
     or not any(c.isalpha() for c in password)
     or not any(c.isdigit() for c in password)
  ):
    return jsonify({
      "error" : "password must have minimum 10 and maximum 128 characters, and must contain atleast one character and a number"
      }), 400
 
  pwd_hash = ph.hash(password)
  #store in db
  con = get_db_connection()
  cur = con.cursor()
  cur.execute('''
  insert into student(
  username,
  email, 
  pwd_hash,
  branch, 
  section
  )
  values(%s, %s, %s, %s, %s)''',
  (username, email, pwd_hash, branch, section)
  )
  con.commit()
  cur.close()
  con.close()
  return "user registered successfully", 200

@auth_bp.route('/login', methods = ["POST"])
def login():
  data = request.get_json()
  email = data.get("email")
  pwd = data.get("password")
  if not email or not pwd:
        return jsonify({"error": "Invalid email or password"}), 401
  con = get_db_connection()
  cur = con.cursor()
  cur.execute("select stud_id, pwd_hash from student where email = %s", (email,))
  stud = cur.fetchone()
  if stud is None:
        cur.close()
        con.close()
        return jsonify({"error": "Invalid email or password"}), 401
  id, pwd_hash = stud
  try:
    ph.verify(pwd_hash, pwd)
  except Exception:
        cur.close()
        con.close()
        return jsonify({"error": "Invalid email or password"}), 401

  cur.close()
  con.close()
  now = datetime.now(timezone.utc)
  access_token = jwt.encode(
    {
      "stud_id" : id,
      "type" : "access",
      "exp" : now + timedelta(hours = 3)
    },
    secret,
    algorithm = 'HS256'

  )

  refresh_jti = str(uuid.uuid4())
  refresh_exp = now + timedelta(days=7)
  refresh_token = jwt.encode(
        {
            "stud_id": id,
            "type": "refresh",
            "jti": refresh_jti,
            "exp": refresh_exp
        },
        secret,
        algorithm="HS256"
    )
  con = get_db_connection()
  cur = con.cursor()
  cur.execute("""
    INSERT INTO refresh(jti, stud_id, expires_at)
    VALUES (%s, %s, %s)""",
    (refresh_jti, id, refresh_exp)
    )
  con.commit()
  cur.close()
  con.close()
  
  return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200



@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()

    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "refresh token required"}), 400

    try:
        payload = jwt.decode(
            refresh_token,
            secret,
            algorithms=["HS256"]
        )
    except InvalidTokenError:
        return jsonify({"error": "invalid or expired refresh token"}), 401

    if payload.get("type") != "refresh":
        return jsonify({"error": "invalid token"}), 401

    stud_id = payload.get("stud_id")
    jti = payload.get("jti")

    if not stud_id or not jti:
        return jsonify({"error": "invalid token"}), 401

    con = get_db_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT revoked, expires_at
        FROM refresh
        WHERE jti = %s 
        AND stud_id = %s""", 
       (jti, stud_id)
    )

    session = cur.fetchone()

    cur.close()
    con.close()

    if session is None:
        return jsonify({"error": "invalid refresh token"}), 401

    revoked, expires_at = session

    if revoked:
        return jsonify({"error": "refresh token has been revoked"}), 401

    now = datetime.now(timezone.utc)

    if expires_at <= now:
        return jsonify({"error": "refresh token expired"}), 401

    access_payload = {
        "stud_id": stud_id,
        "type": "access",
        "exp": now + timedelta(minutes=15)
    }

    access_token = jwt.encode(
        access_payload,
        secret,
        algorithm="HS256"
    )

    return jsonify({
        "access_token": access_token
    }), 200