from mysql.connector import connect
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

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

# 사용자 관련 로직
def get_user_by_username(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def create_user(username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                   (username, hashed_password, email))
    conn.commit()
    cursor.close()
    conn.close()

# SQL 실행
def execute_sql_query(sql_query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return columns, rows

# SQL 문제 조회
def get_sql_problems():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sql_problems")
    problems = cursor.fetchall()
    cursor.close()
    conn.close()
    return problems

def get_sql_problem_by_id(problem_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sql_problems WHERE id = %s", (problem_id,))
    problem = cursor.fetchone()
    cursor.close()
    conn.close()
    return problem
