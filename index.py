from flask import Flask, jsonify , request
import psycopg2
import os
import jwt
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET")
jwt = JWTManager(app)
OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400

def db_connection(): 
    db = psycopg2.connect(database=os.environ.get("BD_NAME"),
        user=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
        host=os.environ.get("HOST"),
        port=os.environ.get("PORT")) 
    return db

@app.route('/', methods = ['GET'])
def home():
    return "Welcome to API!"

@app.route('/morsecode', methods=['POST'])
def send_morse_code():

    conn = db_connection()
    cur = conn.cursor()
    data = request.get_json()
    if "l_morse_code" not in data or "l_space" not in data:
        return jsonify({"error": "Invalid input."}), BAD_REQUEST_CODE
    try:
        cur.execute("call get_current_log()")
        if cur.fetchone()['l_space'] == True:
            cur.execute("call database.insert_log(%s, %b)",[data["l_morse_code"], data["l_space"]])
        else:
            cur.execute("call database.update_log(%s, %b)",[data["l_morse_code"], data["l_space"]])
        conn.commit()
    except Exception as e:
        msg = {"exception": str(e)}
        return jsonify(msg), 500
    finally:
        cur.close()
        conn.close()

    return "Success", SUCCESS_CODE


@app.route('/translation', methods=['GET'])
def get_translation():
    conn = db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM mctt.view_log WHERE l_id = (SELECT MAX(l_id) FROM mctt.log)")
    log = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(log), OK_CODE


@app.route('/logs', methods=['GET'])
def get_logs():
    conn = db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM mctt.view_log")
    logs = []
    for entry in cur.fetchall():
        e = { 
            "l_id": entry[0],
            "l_timestamp": entry[1],
            "l_morse_code": entry[2], 
            "l_translation": entry[3],
            "l_space": entry[4]
        }
        logs.append(e)

    cur.close()
    conn.close()

    return jsonify(logs), OK_CODE


if __name__ == "__main__":
    app.run()