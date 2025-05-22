from fastapi import HTTPException, Form
from fastapi.responses import RedirectResponse
from models import create_user, get_user_by_username, execute_sql_query, get_sql_problems, get_sql_problem_by_id
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 회원가입 처리
async def register_user(username: str, password: str, email: str):
    user = get_user_by_username(username)
    if user:
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    create_user(username, password, email)
    return {"message": "User created successfully."}

# 로그인 처리
async def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not pwd_context.verify(password, user[2]):  # 비밀번호 확인
        raise HTTPException(status_code=400, detail="Invalid username or password.")
    return user

# SQL 쿼리 실행
async def execute_sql(sql_query: str):
    columns, rows = execute_sql_query(sql_query)
    return columns, rows

# SQL 문제 조회
async def get_challenges():
    return get_sql_problems()

# SQL 문제 상세 조회
async def get_challenge_detail(problem_id: int):
    problem = get_sql_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem
