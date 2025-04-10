# 🚗  cars-Server Backend

이 프로젝트는 중고차 가격 예측 웹 서비스의 **백엔드 서버** 역할을 수행합니다. Django 기반의 REST API 서버가 Kafka를 통해 FastAPI 기반의 AI 서버와 통신하며, Elasticsearch를 이용한 차량 데이터 검색 기능도 제공합니다.

---

## 🌐 아키텍처 개요
![Image](https://github.com/user-attachments/assets/56c227cc-c999-4f20-84d9-b9359432a58a)

- 차량 검색 흐름
```
사용자
   ↓
Nginx  →  React 프론트엔드 → Django (REST API)
                                     ↓ Elasticsearch 쿼리 전송
                             Elasticsearch (차량 인덱스 검색)
                                     ↓ 검색 결과 반환
사용자  ←  React 프론트엔드 ← Django (REST API)
```

- 중고차 가격 예측 흐름
```
사용자
   ↓
Nginx  →  React 프론트엔드 → Django (REST API) 
                                     ↓ Kafka 요청 발행
                                  Kafka (중계)
                                     ↓ Kafka 요청 수신
                            FastAPI (AI 예측 서버: PyTorch 모델 기반)
                                     ↓ Kafka 응답 발행
                                  Kafka (중계)
                                     ↓ Kafka 응답 수신
사용자  ←  React 프론트엔드 ← Django (REST API)          
```
---

## 기술 스택 및 구성

- **Django**: 사용자 API 요청 수신 및 처리
- **Kafka**: 메시지 브로커 (요청-응답 구조 비동기 처리)
- **Elasticsearch**: 차량 필터 검색, 정렬, 페이지네이션 처리
- **Kibana**: Elasticsearch 시각화
- **Docker**: 전체 서비스 컨테이너화
- **ASGI**: Django를 비동기 처리로 구동하기 위해 uvicorn 사용

---
## 실행 방법 (개발)
```
pip install --no-cache-dir -r requirements.txt
```
```
# 개발 환경 
$env:DJANGO_SETTINGS_MODULE="config.settings.dev"
# 실행 명령어
uvicorn config.asgi:application --host 127.0.0.1 --port 8000
```
## 배포 방법

### 1. Dockerfile 기반 빌드

```
docker build -t cars-server .
```
### 2. 컨테이너 실행 명령어

```
docker run -d \
  --name cars-server \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /data/docker/cars-server:/app \
  --env-file /data/docker/cars-server/.env.prod \
  cars-server
```

---

## 주요 기능

### Django (API 서버)
- 프론트엔드로부터 차량 정보 수신
- Kafka Producer로 `car-predict-request` 토픽에 메시지 발행
- Kafka Consumer로 `car-predict-response` 응답을 수신하여 사용자에게 반환

### Kafka 리스너 백그라운드 실행
- Django는 asgi.py 실행 시점에 Kafka 리스너를 백그라운드에서 자동 실행
- FastAPI 쪽 로컬 예측 서버는 Kafka Consumer로 계속 대기
- 메시지가 들어오면 예측 수행 후 `car-predict-response`로 결과 반환
- Django는 UUID 기반으로 요청/응답 매칭 처리
- Kafka-FastAPI-Django 간 연결 정상 작동 여부를 확인하기 위해 헬스 체크 (/train/health/)

### Elasticsearch 연동
- 브랜드별 평균 가격, 연식별 감가 추이 
- `/cars/filter-search/`: 브랜드, 모델, 가격, 연식, 연료타입 필터 검색
- Kibana로 검색 인사이트 시각화 가능

---

## ASGI (Uvicorn) 사용 이유

- Kafka 및 FastAPI와의 비동기 통신을 위해 WSGI가 아닌 **ASGI 기반 서버** 필요
- `uvicorn`을 통해 Django를 비동기로 실행 → Kafka Consumer, API 응답 모두 효율적으로 처리 가능

---

## Kafka 구성

- **car-predict-request**: Django → FastAPI (요청)
- **car-predict-response**: FastAPI → Django (응답)
- 완전한 비동기 구조로, 예측 서버의 응답 지연에도 Django가 블로킹되지 않음

---

© 2025 [cars 개인 프로젝트](https://cars.joon-develop.com/)