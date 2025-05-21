from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from mysql.connector import connect
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

# FastAPI 인스턴스 생성
app = FastAPI()

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MySQL 연결 함수

def get_db_connection():
    return connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# 사용자 정보 모델 (Pydantic)
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserInDB(UserCreate):
    hashed_password: str

# 회원가입 엔드포인트
@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    hashed_password = pwd_context.hash(password)  # 비밀번호 해싱
    
    # MySQL 연결
    conn = get_db_connection()
    cursor = conn.cursor()

    # 중복된 사용자 확인
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken."})
    
    # 사용자 추가
    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
    conn.commit()
    cursor.close()
    conn.close()

    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# 로그인 엔드포인트
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # MySQL 연결
    conn = get_db_connection()
    cursor = conn.cursor()

    # 사용자 정보 조회
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user or not pwd_context.verify(password, user[2]):  # 비밀번호 확인
        cursor.close()
        conn.close()
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."})

    # 로그인 성공 시
    cursor.close()
    conn.close()

    # 로그인 성공 시 SQL 페이지로 리디렉션
    return RedirectResponse(url="/sql", status_code=302)
    # return templates.TemplateResponse("welcome.html", {"request": request, "username": username})

# SQL 쿼리 실행 엔드포인트
@app.post("/execute_sql", response_class=HTMLResponse)
async def execute_sql(request: Request, sql_query: str = Form(...)):
    try:
        # DB 연결
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)  # 쿼리 실행
        columns = [desc[0] for desc in cursor.description]  # 컬럼 이름 가져오기
        rows = cursor.fetchall()  # 결과 가져오기
        conn.commit()
        cursor.close()
        conn.close()

        # 결과 출력
        # return templates.TemplateResponse("sql_page.html", {"request": request, "result": result, "error": None})
        return templates.TemplateResponse("sql_page.html", {"request": request,
        "columns": columns, "rows": rows, "error": None})

    except Exception as e:
        return templates.TemplateResponse("sql_page.html", {"request": request, "result": None, "error": str(e)})


# 로그인 화면 (GET 요청)
@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# 회원가입 화면 (GET 요청)
@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

# SQL 쿼리 실행 페이지
@app.get("/sql", response_class=HTMLResponse)
async def sql_page(request: Request):
    return templates.TemplateResponse("sql_page.html", {"request": request, "result": None, "error": None})