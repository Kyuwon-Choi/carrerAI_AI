# 모듈화된 이력서 PDF 변환 서비스

Spring 백엔드와 통신하는 Flask 기반 이력서 PDF 변환 서비스입니다. 코드가 기능별로 모듈화되어 있어 유지보수와 확장이 용이합니다.

## 프로젝트 구조

```
carrerAI_AI/
├── app.py                 # 기존 단일 파일 앱
├── app_new.py            # 새로운 모듈화된 앱
├── test_client.py        # 기존 테스트 클라이언트
├── test_client_new.py    # 새로운 테스트 클라이언트
├── requirements.txt      # 의존성 파일
├── config/              # 설정 관련
│   ├── __init__.py
│   └── settings.py      # 애플리케이션 설정
├── services/            # 비즈니스 로직
│   ├── __init__.py
│   └── pdf_service.py   # PDF 관련 서비스
├── utils/               # 유틸리티 함수들
│   ├── __init__.py
│   └── file_utils.py    # 파일 관련 유틸리티
├── routes/              # API 라우트들
│   ├── __init__.py
│   └── pdf_routes.py    # PDF 관련 API 라우트
└── uploads/             # 업로드된 파일 저장소
```

## 주요 기능

### 1. PDF 텍스트 추출
- PDF 파일을 업로드하여 텍스트로 변환
- `pdfplumber` 라이브러리 사용

### 2. 이력서 PDF 생성
- JSON 형태의 이력서 데이터를 받아 PDF로 변환
- `reportlab` 라이브러리 사용
- 기본 폰트(Helvetica) 사용으로 호환성 확보

### 3. 통합 API
- JSON 데이터 또는 파일 업로드 모두 지원
- Content-Type에 따라 자동 처리

## 설치 및 실행

### 1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서비스 실행

#### 기존 단일 파일 버전
```bash
python app.py
```

#### 새로운 모듈화된 버전
```bash
python app_new.py
```

### 4. 테스트 실행
```bash
# 기존 테스트
python test_client.py

# 새로운 테스트
python test_client_new.py
```

## API 엔드포인트

### 헬스 체크
```
GET /health
```

### PDF 텍스트 추출
```
POST /pdf-to-text
Content-Type: multipart/form-data
```

### 이력서 PDF 생성
```
POST /text-to-pdf
Content-Type: application/json
```

### 통합 이력서 변환
```
POST /convert-resume
Content-Type: application/json 또는 multipart/form-data
```

## 설정

`config/settings.py`에서 다음 설정을 변경할 수 있습니다:

- **포트**: `PORT = 5002`
- **호스트**: `HOST = '0.0.0.0'`
- **최대 파일 크기**: `MAX_CONTENT_LENGTH = 16MB`
- **PDF 폰트**: `PDF_FONT_NAME = 'Helvetica'`

## 모듈화의 장점

### 1. 유지보수성
- 기능별로 코드가 분리되어 있어 수정이 용이
- 각 모듈의 책임이 명확히 구분됨

### 2. 확장성
- 새로운 기능 추가 시 해당 모듈만 수정
- 다른 서비스 추가 시 새로운 서비스 클래스 생성

### 3. 테스트 용이성
- 각 모듈을 독립적으로 테스트 가능
- 단위 테스트 작성이 쉬움

### 4. 재사용성
- 서비스 클래스들을 다른 프로젝트에서 재사용 가능
- 설정을 다른 환경에 맞게 쉽게 변경

## 새로운 기능 추가 방법

### 1. 새로운 서비스 추가
```python
# services/new_service.py
class NewService:
    @staticmethod
    def new_function():
        # 새로운 기능 구현
        pass
```

### 2. 새로운 라우트 추가
```python
# routes/new_routes.py
from flask import Blueprint

new_bp = Blueprint('new', __name__)

@new_bp.route('/new-endpoint', methods=['GET'])
def new_endpoint():
    # 새로운 엔드포인트 구현
    pass
```

### 3. 메인 앱에 등록
```python
# app_new.py
from routes.new_routes import new_bp

app.register_blueprint(new_bp)
```

## 환경 변수

다음 환경 변수를 설정할 수 있습니다:

- `SECRET_KEY`: Flask 시크릿 키
- `DEBUG`: 디버그 모드 (True/False)
- `HOST`: 서버 호스트
- `PORT`: 서버 포트

## Docker 실행

```bash
docker-compose up --build
```

## 라이센스

MIT License 