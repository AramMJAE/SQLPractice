from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import get_db_connection
from controllers import register_user, authenticate_user, execute_sql, get_challenges, get_challenge_detail
from typing import Optional  # Optional을 가져옵니다.

app = FastAPI()

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    result = await register_user(username, password, email)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    await authenticate_user(username, password)
    return RedirectResponse(url="/schema", status_code=302)

@app.get("/schema", response_class=HTMLResponse)
async def schema_info(request: Request):
    return templates.TemplateResponse("schema_info.html", {"request": request})

# SQL 문제 페이지 (문제 목록)
@app.get("/sql_challenges", response_class=HTMLResponse)
async def sql_challenge_page(request: Request, problem_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sql_problems")
    problems = cursor.fetchall()  # 문제 목록을 가져옵니다

    cursor.close()
    conn.close()

    # problem_id가 존재하면 해당 문제의 상세 페이지로 리디렉션
    if problem_id:
        return RedirectResponse(url=f"/sql_challenges/{problem_id}", status_code=302)

    # 문제 목록을 선택할 수 있는 페이지로 반환
    return templates.TemplateResponse("sql_challenges.html", {"request": request, "problems": problems})

# SQL 문제 상세 페이지
@app.get("/sql_challenges/{problem_id}", response_class=HTMLResponse)
async def sql_challenge_detail(request: Request, problem_id: int):
    # 문제의 상세 정보 가져오기
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sql_problems WHERE id = %s", (problem_id,))
    problem = cursor.fetchone()
    cursor.close()
    conn.close()

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 문제 상세 페이지 반환
    return templates.TemplateResponse("sql_challenge_detail.html", {"request": request, "problem": problem})

@app.post("/execute_sql", response_class=HTMLResponse)
async def execute_sql(request: Request, sql_query: str = Form(...)):
    try:
        # DB 연결
        conn = get_db_connection()
        cursor = conn.cursor()

        # 쿼리 실행
        cursor.execute(sql_query)  # 쿼리 실행
        columns = [desc[0] for desc in cursor.description]  # 컬럼 이름 가져오기
        rows = cursor.fetchall()  # 결과 가져오기
        conn.commit()
        cursor.close()
        conn.close()

        # 결과 반환
        return templates.TemplateResponse("sql_page.html", {
            "request": request,
            "columns": columns,
            "rows": rows,
            "error": None
        })

    except Exception as e:
        # 예외 처리
        return templates.TemplateResponse("sql_page.html", {
            "request": request,
            "columns": None,
            "rows": None,
            "error": str(e)
        })


@app.get("/sql", response_class=HTMLResponse)
async def sql_page(request: Request):
    return templates.TemplateResponse("sql_page.html", {"request": request, "rows": None, "columns": None, "error": None})
