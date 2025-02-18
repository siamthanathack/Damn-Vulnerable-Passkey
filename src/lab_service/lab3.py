# This project was developed by Siam Thanat Hack Co., Ltd. (STH).
# Website: https://sth.sh  
# Contact: pentest@sth.sh
from flask import Blueprint, render_template, request, Response
from webauthn import (
    generate_authentication_options,
    verify_authentication_response
)
from webauthn.helpers import (
    options_to_json,
    parse_authentication_credential_json
)
import os

from lab_service import labs_info
from database_service.database_lab.lab3.db_lab3 import get_db_connection, init_db

# Define a Blueprint for Lab 3
lab3_bp = Blueprint('lab3', __name__, template_folder='templates')

# Define route for Lab 3
@lab3_bp.route('/lab3')
def lab3_home():
    init_db()
    return render_template('labs/lab3/index.html', title="Lab 3", lab=labs_info[3])

@lab3_bp.route('/lab3/list_user')
def lab3_list_user():
    return render_template('labs/lab3/list_user.html', title="Lab 3", lab=labs_info[3])

@lab3_bp.route('/lab3/login')
def lab3_login():
    return render_template('labs/lab3/login.html', title="Lab 3", lab=labs_info[3])

@lab3_bp.route('/lab3/api/search_user', methods=['POST'])
def searchUser():
    return search_user(request.json['query'])

@lab3_bp.route('/lab3/api/authentication_start', methods=['POST'])
def authenticationStart():
    username = request.json['username']
    existing_pubkeys = get_available_public_key_by_username(username)
    if not existing_pubkeys:
        return "This username does not have a Passkey registered!", 404
    resp = generate_authentication_options(
        rp_id = os.getenv("RP_ID")
    )
    store_challenge(username, resp.challenge)
    return Response(options_to_json(resp), content_type='application/json')

@lab3_bp.route('/lab3/api/authentication_verify', methods=['POST'])
def authenticationVerify():
    username = request.json['username']
    credential = parse_authentication_credential_json(request.json['response'])
    expected_challenge = get_challenge(username)
    credential_public_key, credential_current_sign_count = get_pubkey_and_counter(username, credential.raw_id)
    resp = verify_authentication_response(
        credential = credential,
        expected_challenge = expected_challenge,
        expected_rp_id = os.getenv("RP_ID"),
        expected_origin = os.getenv("ORIGIN"),
        credential_public_key = credential_public_key,
        credential_current_sign_count = credential_current_sign_count
    )
    delete_challenge(username)
    return login(username)

def get_challenge(username: str):
    with get_db_connection() as conn:
        res = conn.execute('''
            SELECT * FROM challenges WHERE username = ? ORDER BY id DESC
        ''', (username,)).fetchone()
        if res:
            return res['challenge']
        else:
            raise ValueError("Challenge not found") 

def store_challenge(username: str, challenge: bytes):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO challenges (username, challenge) VALUES (?, ?)
        ''', (username, challenge,))
        conn.commit()

def delete_challenge(username: str):
    with get_db_connection() as conn:
        conn.execute('''
            DELETE FROM challenges WHERE username = ?
        ''', (username,))
        conn.commit()

def get_pubkey_and_counter(username: str, raw_id: bytes):
    with get_db_connection() as conn:
        res = conn.execute('''
            SELECT * FROM pubkeys WHERE username = ? AND raw_id = ?
        ''', (username, raw_id,)).fetchone()
        if res:
            return res['public_key'], res['counter']
        else:
            raise ValueError("Public key not found") 

def store_pubkey(username: str, raw_id: bytes, public_key: bytes):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO pubkeys (username, raw_id, public_key, counter) VALUES (?, ?, ?, 0)
        ''',(username, raw_id, public_key,))
        conn.commit()

def get_available_public_key_by_username(username: str):
    with get_db_connection() as conn:
        res = conn.execute('''
            SELECT * FROM pubkeys WHERE username = ?
        ''', (username,)).fetchall()
        if res:
            return [item['raw_id'] for item in res]
        else:
            return []

def search_user(query: str):
    with get_db_connection() as conn:
        conn.execute("PRAGMA query_only = ON;")
        res = conn.execute(f'''
            SELECT * FROM users WHERE username LIKE '%{query}%' ORDER BY id ASC
        ''').fetchall()
        if res:
            return [
                {
                    "username": item['username']
                } for item in res
            ]
        else:
            return []

def login(username):
    return f"Hello Mr. {username}. Here is your secret message: {os.getenv('FLAG3')}"
