// This project was developed by Siam Thanat Hack Co., Ltd. (STH).
// Website: https://sth.sh  
// Contact: pentest@sth.sh
async function register() {
    const username = document.getElementById("username").value.trim();
    if (username) {
        const apiRegOptsResp = await fetch('/lab2/registration_start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                user_verification: 'preferred',
                attestation: 'none',
                attachment: 'platform',
                algorithms: ['es256', 'rs256'],
                discoverable_credential: 'preferred'
            })
        });
        if (apiRegOptsResp.status != 200) {
            alert(await apiRegOptsResp.text());
            return;
        }
        const registrationOptionsJSON = await apiRegOptsResp.json();
        const regResp = await startRegistration(registrationOptionsJSON);
        const apiRegVerResp = await fetch('/lab2/registration_verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: username,
              response: regResp,
            }),
        });
        alert(await apiRegVerResp.text())
    } else {
        alert("Please enter a valid username.");
    }
}

async function authenticate() {
    const username = document.getElementById("username").value.trim();
    if (username) {
        const apiAuthOptsResp = await fetch('/lab2/authentication_start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username
            })
        });
        if (apiAuthOptsResp.status != 200) {
            alert(await apiAuthOptsResp.text());
            return;
        }
        const authenticationOptionsJSON = await apiAuthOptsResp.json();
        const authResp = await startAuthentication(authenticationOptionsJSON);
        const apiAuthVerResp = await fetch('/lab2/authentication_verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: username,
              response: authResp,
            }),
        });
        alert(await apiAuthVerResp.text())
    } else {
        alert("Please enter a valid username.");
    }
}
