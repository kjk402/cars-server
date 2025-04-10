FROM python:3.10-slim

# 환경 세팅
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# 필요 파일 복사
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 전체 프로젝트 복사
COPY . .

# Static 파일 처리 (선택)
RUN mkdir -p /app/static && python manage.py collectstatic --noinput || true

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
