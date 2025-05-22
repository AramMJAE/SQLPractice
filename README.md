# SQLPractice

###  Railway를 이용해서 MySQL의 Classicmodels DB 형태와 데이터를 가지고 SQL 쿼리를 테스트를 할 수 있습니다.

## 설치 및 실행 방법

1. **가상환경 생성 및 패키지 설치**
```bash
uv venv --python 3.11
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
uv pip install -r requirements.txt
```

2. **FastAPI 서버 실행**
```bash
uvicorn main:app --reload
```

3. **로컬 환경**
- http://127.0.0.1:8000 에서 확인 가능

4. **Vercel 환경** (진행중)
- https://sql-practice-tau.vercel.app/

