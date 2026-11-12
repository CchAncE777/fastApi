# python -m uvicorn fisrt_api:app --reload
# https://localhost:8443/

from datetime import datetime, timedelta

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pandas as pd
import hashlib
import datetime
import tempfile
import uvicorn

SESSION_LIFETIME = timedelta(minutes=3)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def generate_self_signed_cert():
    # Генерация ключа
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BY"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Minsk"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Minsk"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FastAPI In-Memory"),
        x509.NameAttribute(NameOID.COMMON_NAME, "666"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now())
        .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Сохраняем во временные файлы
    key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    cert_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")

    key_file.write(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    key_file.close()

    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    cert_file.close()

    return key_file.name, cert_file.name

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="krivobotkrivobotkrivobot")

white_urls = ["/", "/login", "/logout", "/register"]

# Маршрутизация приложения
@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name ="based_main.html")

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    print(datetime.now(), request.session.get('session_starttime'))
    if datetime.now() - datetime.fromisoformat(request.session.get('session_starttime')) >= SESSION_LIFETIME:
        # грохнуть сессию
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)        
    else:
        request.session['session_starttime'] = str(datetime.now())
    username = request.session.get('username')
    password_hash = request.session.get('password_hash')
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request=request, 
                                      name="home.html", 
                                      context={'username': username, 
                                               'password_hash': password_hash})


users = [{'username' : 'admin', 'password' : hash_password('1111' + 'admin')}]
df = pd.DataFrame(users)
df.to_csv("krivousers.csv", index=False, encoding="utf-8")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.post("/register")
def register(request: Request,
            password: str = Form(...), 
            username: str = Form(...)):
    res = ''
    df = pd.read_csv('krivousers.csv')
    users_new = df.to_dict(orient="records")
    print(users_new)
    for i in users_new:
        if username == i['username']:
            res = 'ужес exist'
            break
    if res == 'ужес exist':
        return templates.TemplateResponse(name="register.html",
                                        request=request, 
                                        context={"error": res})
    else:
        new_user = pd.DataFrame([{'username' : username, 'password' : hash_password(password + username)}])
        new_user.to_csv('krivousers.csv', mode="a", index=False, header=False, encoding="utf-8")
        request.session['username'] = username
        request.session['password_hash'] = hash_password(password + username)
        request.session['session_starttime'] = str(datetime.now())
        response = RedirectResponse(url=f"/home", status_code=302)
        return response
    
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login(request: Request,
          password: str = Form(...), 
          username: str = Form(...) 
          ):
    df = pd.read_csv('krivousers.csv')
    users_new = df.to_dict(orient="records")
    print(users_new)
    res = 'neverno'
    for i in users_new:
        if username == i['username'] and hash_password(password + username) == i['password'] :
            res = 'успешно'
            break

    if res == 'успешно':
        request.session["username"] = username
        request.session['password_hash'] = hash_password(password + username)
        request.session['session_starttime'] = str(datetime.now())
        response = RedirectResponse(url=f"/home", status_code=302)
        return response
    else:
        return templates.TemplateResponse({"request": request, 
                                        "error": "Неверный пароль или логин"},
                                        name="login.html")



@app.get("/404", response_class=HTMLResponse)
def _404_page(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")

@app.get('/403', response_class=HTMLResponse)
def _403_page(request: Request):
    return templates.TemplateResponse(request=request, name='403.html')

@app.get("/")
def read_root():
    return {"message": "Hello over HTTPS (in-memory cert)!"}

if __name__ == "__main__":
    key_path, cert_path = generate_self_signed_cert()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path,
    )