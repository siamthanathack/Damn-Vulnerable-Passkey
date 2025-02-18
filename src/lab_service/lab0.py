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
    parse_authentication_credential_json
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor
)
import secrets
import os

from lab_service import labs_info
from database_service.database_lab.lab0.db_lab0 import get_db_connection, init_db

# Define a Blueprint for Lab 0
lab0_bp = Blueprint('lab0', __name__, template_folder='templates')

# Define route for Lab 0
@lab0_bp.route('/lab0')
def lab0():
    init_db()
    return render_template('labs/lab0/index.html', title="Lab 0", lab=labs_info[0])

@lab0_bp.route('/lab0/registration_start', methods=['POST'])
def registrationStart():
    username = request.json['username']
    existing_pubkeys = get_available_public_key_by_username(username)
    resp = generate_registration_options(
        rp_id = os.getenv("RP_ID"),
        rp_name = os.getenv("RP_NAME"),
        user_name = username,
        user_id = secrets.token_bytes(32),
        exclude_credentials = [
            PublicKeyCredentialDescriptor(
                id = pubkey
            ) for pubkey in existing_pubkeys
        ]
    )
    store_challenge(username, resp.challenge)
    return Response(options_to_json(resp), content_type='application/json')

@lab0_bp.route('/lab0/registration_verify', methods=['POST'])
def registrationVerify():
    username = request.json['username']
    credential = parse_registration_credential_json(request.json['response'])
    expected_challenge = get_challenge(username)
    resp = verify_registration_response(
        credential = credential,
        expected_challenge = expected_challenge,
        expected_rp_id = os.getenv("RP_ID"),
        expected_origin = os.getenv("ORIGIN")
    )
    store_pubkey(username, resp.credential_id, resp.credential_public_key)
    delete_challenge(username)
    return "Registration Completed"

@lab0_bp.route('/lab0/authentication_start', methods=['POST'])
def authenticationStart():
    username = request.json['username']
    existing_pubkeys = get_available_public_key_by_username(username)
    if not existing_pubkeys:
        return "This username does not have a Passkey registered!", 404
    resp = generate_authentication_options(
        rp_id = os.getenv("RP_ID"),
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                id = pubkey
            ) for pubkey in existing_pubkeys
        ]
    )
    store_challenge(username, resp.challenge)
    return Response(options_to_json(resp), content_type='application/json')

@lab0_bp.route('/lab0/authentication_verify', methods=['POST'])
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

def login(username):
    return f"Authentication completed! Welcome Mr. {username}"
