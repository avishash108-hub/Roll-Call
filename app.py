from dotenv import load_dotenv
load_dotenv()
from os import name
from re import sub
from flask import Flask
from flask_cors import CORS
from auth.routes import auth_bp
from backend.routes.subjects import sub_bp
from backend.routes.attendance import att_bp
from backend.routes.notes import notes_bp
from backend.routes.timetable import tt_bp
from backend.routes.predict import pred_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(auth_bp)
app.register_blueprint(sub_bp)
app.register_blueprint(att_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(tt_bp)
app.register_blueprint(pred_bp)

@app.route('/')
def home():
    return "my flask is running"





if __name__ == '__main__':
    app.run(debug=True)
