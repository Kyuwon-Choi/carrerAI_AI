# CareerAI 백엔드 서비스

Flask 기반의 이력서 PDF 변환 및 기업 확률 예측 서비스입니다.

## 주요 기능

### 1. 이력서 PDF 변환
- JSON 데이터를 기반으로 이력서 PDF 생성
- 한글 폰트 지원 (macOS 기본 폰트 사용)
- ReportLab을 사용한 고품질 PDF 생성

### 2. 기업 확률 예측
- 사용자 프로필 데이터를 기반으로 기업 입사 확률 예측
- 머신러닝 모델 연동 구조 제공
- 예측 결과에 따른 개인화된 추천사항 제공

## 프로젝트 구조

```
carrerAI_AI/
├── app.py                 # 메인 애플리케이션
├── test_client.py         # 테스트 클라이언트
├── requirements.txt       # 의존성 목록
├── config/               # 설정 파일
│   └── settings.py
├── services/             # 비즈니스 로직
│   ├── pdf_service.py    # PDF 변환 서비스
│   └── prediction_service.py  # 예측 서비스
├── routes/               # API 라우트
│   ├── pdf_routes.py     # PDF 관련 API
│   ├── prediction_routes.py  # 예측 관련 API
│   └── swagger_routes.py # Swagger 문서
├── utils/                # 유틸리티
│   └── helpers.py
├── models/               # 머신러닝 모델 (추후 추가)
└── uploads/              # 업로드 파일 저장소
```

## 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 3. 테스트 실행
```bash
python test_client.py
```

## API 문서

Swagger UI를 통해 API 문서를 확인할 수 있습니다:
- URL: `http://localhost:5000/docs`

## API 엔드포인트

### PDF 변환 API

#### POST /api/pdf/convert
JSON 데이터를 이력서 PDF로 변환합니다.

**요청 예시:**
```json
{
  "name": "홍길동",
  "age": 28,
  "experience": 3.5,
  "skills": ["Python", "Flask", "React", "Docker"],
  "education": "컴퓨터공학과 졸업",
  "etc": "프로젝트 경험 다수"
}
```

**응답:** PDF 파일 (binary)

### 기업 확률 예측 API

#### POST /api/prediction/predict
사용자 데이터를 기반으로 기업 입사 확률을 예측합니다.

**요청 예시:**
```json
{
  "name": "김개발",
  "age": 25,
  "experience": 2.0,
  "skills": ["Java", "Spring", "MySQL"],
  "education": "정보통신공학과 졸업",
  "etc": "스타트업 경험 1년"
}
```

**응답 예시:**
```json
{
  "success": true,
  "probability": 0.75,
  "confidence": 0.85,
  "recommendations": [
    "포트폴리오를 더욱 다양화해보세요",
    "최신 기술 트렌드를 학습하세요",
    "자기소개서를 개선해보세요"
  ],
  "user_data": {
    "name": "김개발",
    "age": 25,
    "experience": 2.0,
    "skills": ["Java", "Spring", "MySQL"],
    "education": "정보통신공학과 졸업",
    "etc": "스타트업 경험 1년"
  }
}
```

#### GET /api/prediction/model/info
현재 로드된 모델의 정보를 조회합니다.

**응답 예시:**
```json
{
  "model_loaded": true,
  "model_path": "models/",
  "model_type": "기업 확률 예측 모델",
  "version": "1.0.0"
}
```

#### POST /api/prediction/model/load
예측 모델을 로드합니다.

**파라미터:**
- `model_name` (선택): 모델 파일명

#### GET /api/prediction/health
예측 서비스의 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "prediction_service"
}
```

## 모델 연동

### 현재 상태
- 예측 서비스 구조가 구현되어 있습니다
- 임시 예측 로직이 포함되어 있습니다
- 실제 머신러닝 모델은 추후 추가 예정입니다

### 모델 추가 방법
1. `models/` 디렉토리에 모델 파일을 추가
2. `services/prediction_service.py`의 `load_model()` 메서드에서 실제 모델 로드 로직 구현
3. `predict_company_probability()` 메서드에서 실제 예측 로직 구현

### 예시 모델 로드 코드
```python
# joblib을 사용한 경우
import joblib
self.model = joblib.load(f"{self.model_path}/{model_name}")

# pickle을 사용한 경우
import pickle
with open(f"{self.model_path}/{model_name}", 'rb') as f:
    self.model = pickle.load(f)
```

## 개발 환경

- Python 3.8+
- Flask 3.0.0
- ReportLab 4.0.7
- Flask-RESTX 1.3.0

## 배포

### Docker 사용
```bash
# 이미지 빌드
docker build -t careerai-backend .

# 컨테이너 실행
docker run -p 5000:5000 careerai-backend
```

### Docker Compose 사용
```bash
docker-compose up -d
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 