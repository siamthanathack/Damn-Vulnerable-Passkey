# Damn Vulnerable Passkey

Damn Vulnerable Passkey (DVP) is a deliberately insecure WebAuthn/Passkey training platform designed to help security professionals and enthusiasts explore, understand, and exploit various vulnerabilities in modern authentication schemes. By simulating real-world scenarios with misconfigurations, improper server-side checks, and weak client implementations, DVP allows hands-on practice in identifying and mitigating threats that could compromise WebAuthn-based authentication systems.

## Demo: [https://damn-vulnerable-passkey.p7z.pw](https://damn-vulnerable-passkey.p7z.pw)

## Setup .env file
```dot
RP_ID="localhost"
RP_NAME="localhost"
PORT="5000"
ORIGIN="http://localhost:5000"
DEBUG="True"
FLAG1="STH{***********}"
FLAG2="STH{***********}"
FLAG3="STH{***********}"
```

## Prerequisite
```bash
# Tested on Python 3.13.1
pyenv install 3.13.1
pyenv virtualenv 3.13.1 passkey
pyenv activate passkey
pip install -r requirements.txt
```

## Start server
```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000)

---

## Credits

Developed by **Siam Thanat Hack Co., Ltd. (STH)**
**Website**: [https://sth.sh](https://sth.sh)
**Contact**: pentest@sth.sh

---

Happy hacking!