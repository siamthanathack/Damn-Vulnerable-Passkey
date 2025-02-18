# This project was developed by Siam Thanat Hack Co., Ltd. (STH).
# Website: https://sth.sh  
# Contact: pentest@sth.sh
from flask import Flask, render_template
from dotenv import load_dotenv
import os

from lab_service import labs_info
from lab_service.lab0 import lab0_bp
from lab_service.lab1 import lab1_bp
from lab_service.lab2 import lab2_bp
from lab_service.lab3 import lab3_bp

app = Flask(__name__)

# Load Environment Variables
load_dotenv()

# Register Blueprints (each one corresponds to a separate lab)
app.register_blueprint(lab0_bp)
app.register_blueprint(lab1_bp)
app.register_blueprint(lab2_bp)
app.register_blueprint(lab3_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get-start')
def get_start():
    return render_template('get_start.html')

@app.context_processor
def inject_context():
    return {'labs_info': labs_info}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT")), debug=(os.getenv("DEBUG").strip().lower() == "true"))
