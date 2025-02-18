# lab_info.py - contains attributes for each lab
labs_info = [
    {
        "id": 0,
        "title": "Lab 0: Totally Normal Passkey",
        "description": '''
            This is a normal passkey implementation.<br />
            This lab should not have any vulnerability by design.
        ''',
        "objective": '''
            None
        ''',
        "js_file": "lab0.js"
    },
    {
        "id": 1,
        "title": "Lab 1: Trustworthy Challenge",
        "description": '''
            Obscurity = Security.<br />
            Always trust user input.
        ''',
        "objective": '''
            Successful login as the "admin" user
        ''',
        "js_file": "lab1.js"
    },
    {
        "id": 2,
        "title": "Lab 2: Exclusivity",
        "description": '''
            This website is only accessible if the user possesses a STH Keychain Passkey authenticator.<br />
            According to leaked data, the STH Keychain's aaguid is 84b91d8f-4d2a-417f-ae12-3f8c0d63e052.
        ''',
        "objective": '''
            Successful login as any user
        ''',
        "js_file": "lab2.js"
    },
    {
        "id": 3,
        "title": "Lab 3: Authenticator Private Key Compromised",
        "description": '''
            Something that should not be there, is there.<br />
        ''',
        "objective": '''
            Successful login as the "admin" user
        ''',
        "js_file": "lab3.js"
    }
]
