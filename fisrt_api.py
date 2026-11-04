# python -m uvicorn fisrt_api:app --reload

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

white_urls = ["/", "/login", "/logout", "/register"]

# Маршрутизация приложения
@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name ="based_main.html")

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(request=request, 
                                      name="home.html",
                                      context = {'username': 'Uzver',
                                                 'password_hash': 'asdaad'})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post('/login')
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...)):
    print(request)
    print(username)
    print(password)

    if username == 'Uzver' and password == 'asdaad':
        return RedirectResponse(url="/home", status_code=303)
    else:
        return RedirectResponse(url='/404', status_code=303)

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/404", response_class=HTMLResponse)
def error_page(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")