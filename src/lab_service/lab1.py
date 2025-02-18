# This project was developed by Siam Thanat Hack Co., Ltd. (STH).
# Website: https://sth.sh  
# Contact: pentest@sth.sh
from flask import Blueprint, render_template, request, Response
from webauthn import (
    generate_registration_options, 
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response
)
from webauthn.helpers import (
    options_to_json,
    parse_registration_credential_json,
    parse_authentication_credential_json,
    base64url_to_bytes,
    bytes_to_base64url
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor
)
import secrets
import os
import json
import string
import random

from lab_service import labs_info
from database_service.database_lab.lab1.db_lab1 import get_db_connection, init_db

# Define a Blueprint for Lab 1
lab1_bp = Blueprint('lab1', __name__, template_folder='templates')

def gen_random_string(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Define route for Lab 1
@lab1_bp.route('/lab1')
def lab1():
    init_db()
    return render_template('labs/lab1/index.html', title="Lab 1", lab=labs_info[1])

@lab1_bp.route('/lab1/registration_start', methods=['POST'])
def registrationStart():
    username = request.json['username']
    if username == "admin":
        return "Cannot register as admin!", 403
    existing_pubkeys = get_available_public_key_by_username(username)
    resp = generate_registration_options(
        rp_id = os.getenv("RP_ID"),
        rp_name = os.getenv("RP_NAME"),
        user_name = username,
        user_id = secrets.token_bytes(32),
        exclude_credentials = [
            PublicKeyCredentialDescriptor(
                id = base64url_to_bytes(pubkey)
            ) for pubkey in existing_pubkeys
        ]
    )
    store_challenge(username, bytes_to_base64url(resp.challenge))
    return Response(options_to_json(resp), content_type='application/json')

@lab1_bp.route('/lab1/registration_verify', methods=['POST'])
def registrationVerify():
    username = request.json['username']
    credential = parse_registration_credential_json(request.json['response'])
    expected_challenge = get_challenge(username)
    resp = verify_registration_response(
        credential = credential,
        expected_challenge = base64url_to_bytes(expected_challenge),
        expected_rp_id = os.getenv("RP_ID"),
        expected_origin = os.getenv("ORIGIN")
    )
    store_pubkey(username, bytes_to_base64url(resp.credential_id), bytes_to_base64url(resp.credential_public_key))
    delete_challenge(username)
    return "Registration Completed"

@lab1_bp.route('/lab1/authentication_start', methods=['POST'])
def authenticationStart():
    username = request.json['username']
    existing_pubkeys = get_available_public_key_by_username(username)
    if not existing_pubkeys:
        return "This username does not have a Passkey registered!", 404
    resp = generate_authentication_options(
        rp_id = os.getenv("RP_ID"),
        challenge = (gen_random_string(62)).encode('utf-8'),
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                id = base64url_to_bytes(pubkey)
            ) for pubkey in existing_pubkeys
        ]
    )
    store_challenge(username, resp.challenge.decode('utf-8'))
    return Response(options_to_json(resp), content_type='application/json')

@lab1_bp.route('/lab1/authentication_verify', methods=['POST'])
def authenticationVerify():
    username = request.json['username']
    credential = parse_authentication_credential_json(request.json['response'])
    credential_public_key, credential_current_sign_count = get_pubkey_and_counter(username, credential.id)
    # Vulnerability: SQL Injection - Step 1 Get "challenge" from user input
    challenge = json.loads(credential.response.client_data_json.decode('utf-8'))['challenge']
    # Verify signature w/o Passkey Raider, arbitrary challenge value should not pass!
    resp = verify_authentication_response(
        credential = credential,
        expected_challenge = base64url_to_bytes(challenge),
        expected_rp_id = os.getenv("RP_ID"),
        expected_origin = os.getenv("ORIGIN"),
        credential_public_key = base64url_to_bytes(credential_public_key),
        credential_current_sign_count = credential_current_sign_count
    )
    # Vulnerability: SQL Injection - Step 2 Perform Base64 decoding and pass to get_username_by_challenge() function
    login_resp = login(get_username_by_challenge(base64url_to_bytes(challenge).decode('utf-8')))
    delete_challenge(username)
    return login_resp

def get_challenge(username: str):
    with get_db_connection() as conn:
        res = conn.execute('''
            SELECT * FROM challenges WHERE username = ? ORDER BY id DESC
        ''', (username,)).fetchone()
        if res:
            return res['challenge']
        else:
            raise ValueError("Challenge not found") 

def store_challenge(username: str, challenge: str):
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

def get_username_by_challenge(challenge: string):
    # Vulnerability: SQL Injection - Step 3 user input incorporate into raw SQL query and execute it as SQL command
    # Exploit:
    # echo  -n "' and 1>2 union select 1,'admin',2 | base64"
    with get_db_connection() as conn:
        conn.execute("PRAGMA query_only = ON;")
        sql = f"SELECT * FROM challenges WHERE challenge = '{challenge}' LIMIT 1"
        print(f"debug: {sql}")
        res = conn.execute(sql).fetchone()
        if res:
            return res['username']
        else:
            raise ValueError("Challenge not found") 

def get_pubkey_and_counter(username: str, raw_id: str):
    with get_db_connection() as conn:
        res = conn.execute('''
            SELECT * FROM pubkeys WHERE username = ? AND raw_id = ?
        ''', (username, raw_id,)).fetchone()
        if res:
            return res['public_key'], res['counter']
        else:
            raise ValueError("Public key not found") 

def store_pubkey(username: str, raw_id: str, public_key: str):
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

def login(username):
    if username != "admin":
        return "Sorry, our system is still in maintenance."
    return f"Hello Mr. {username}. Here is your secret message: {os.getenv('FLAG1')}"
