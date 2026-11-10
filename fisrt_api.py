# python -m uvicorn fisrt_api:app --reload

import hashlib
import csv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

white_urls = ["/", "/login", "/logout", "/register"]
# Маршрутизация приложения
def hash_password(password):
    password_hash = hashlib.sha256(password.encode('utf-8'))
    return password_hash.hexdigest()

@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name ="based_main.html")

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(request=request, 
                                      name='home.html')

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post('/login')
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...)):

    with open("users.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username and row["password"] == hash_password(password):
                    # return RedirectResponse(url="/home", status_code=303)
                    return templates.TemplateResponse(request=request, name='home.html', context={'username' : username, 'password_hash' : hash_password(password)})
                
            return templates.TemplateResponse(request=request, name="404.html")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post('/register')
def register(request: Request,
          username: str = Form(...),
          password: str = Form(...)):
    
    with open("users.csv", mode="a", encoding="utf-8", newline='') as file:
        fieldnames = ['username', 'password']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writerow({'username': username, 
                         'password': hash_password(password)})


    return templates.TemplateResponse(request=request, name="home.html")

@app.get("/404", response_class=HTMLResponse)
def error_page(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")