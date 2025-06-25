# CareerAI API

이력서 PDF 변환 및 기업 확률 예측을 위한 Flask 기반 REST API 서버입니다.

## 주요 기능

- **PDF 텍스트 변환**: PDF 파일에서 텍스트 추출
- **이력서 파싱**: PDF 이력서에서 구조화된 정보 추출
- **AI 기업 확률 예측**: 사용자 데이터를 기반으로 기업별 합격 확률 예측
- **RESTful API**: Swagger 문서화된 REST API 제공

## AI 모델 설정

### 1. 모델 파일 위치

AI 모델 파일들은 `models/` 디렉토리에 위치해야 합니다:

```
models/
├── xgb_model.pkl      # XGBoost 모델 파일
└── label_map.pkl      # 라벨 매핑 파일
```

### 2. 모델 파일 준비

코랩에서 학습한 모델을 다운로드하여 `models/` 디렉토리에 저장하세요:

```python
# 코랩에서 실행
import joblib
import pandas as pd

# 모델 저장
joblib.dump(model, 'xgb_model.pkl')
joblib.dump(label_map, 'label_map.pkl')

# 파일 다운로드
from google.colab import files
files.download('xgb_model.pkl')
files.download('label_map.pkl')
```

### 3. 모델 로드

서버 시작 시 자동으로 모델을 로드하거나, API를 통해 수동으로 로드할 수 있습니다:

```bash
# 모델 로드 API 호출
curl -X POST http://172.16.29.250:5002/api/ai/model/load
```

## API 엔드포인트

### AI 분석 API

#### 기업 확률 분석
```
POST /analyze-probability
POST /api/ai/analyze-probability
```

**요청 데이터:**
```json
{
  "user_id": 1,
  "recruitment_id": 1,
  "job_category": "IT/개발",
  "age": 26,
  "school": 2.0,
  "major": 4.5,
  "gpa": 3.5,
  "language_score": 2,
  "activity_score": 12,
  "internship_score": 10,
  "award_score": 6
}
```

**응답 데이터:**
```json
{
  "success": true,
  "probabilities": {
    "삼성전자": 40.56,
    "SK하이닉스": 26.06,
    "SK이노베이션": 23.51,
    "LG전자": 4.75,
    "현대자동차": 2.42,
    "롯데": 1.59,
    "KT": 0.57,
    "포스코": 0.38,
    "CJ": 0.17
  },
  "top_company": "삼성전자",
  "top_probability": 40.56,
  "message": "분석이 완료되었습니다."
}
```

#### 모델 정보 조회
```
GET /api/ai/model/info
```

#### 모델 로드
```
POST /api/ai/model/load
```

### 기존 API

#### PDF 텍스트 변환
```
POST /documents/convert
POST /api/documents/convert
```

#### 이력서 파싱
```
POST /documents/parse-resume
POST /api/documents/parse-resume
```

## 스프링 연동

### 스프링에서 AI 분석 요청

```java
private Map<String, Double> sendAnalysisRequestToFlask(User user, Recruitment recruitment) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);

    // 분석 요청 데이터 구성
    Map<String, Object> requestData = new HashMap<>();
    requestData.put("user_id", user.getId());
    requestData.put("recruitment_id", recruitment.getId());
    requestData.put("job_category", recruitment.getJobCategory());
    requestData.put("age", user.getAge());
    requestData.put("school", user.getSchoolLabel());
    requestData.put("major", user.getMajorLabel());
    requestData.put("gpa", user.getGpa());
    requestData.put("language_score", user.getLanguageScoreLabel());
    requestData.put("activity_score", user.getActivityScore());
    requestData.put("internship_score", user.getInternshipScore());
    requestData.put("award_score", user.getAwardScore());

    HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestData, headers);

    try {
        ResponseEntity<Map> response = restTemplate.postForEntity(
            flaskServiceUrl + "/analyze-probability", 
            requestEntity, 
            Map.class
        );
        
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            Map<String, Object> result = response.getBody();
            if ((Boolean) result.get("success")) {
                return (Map<String, Double>) result.get("probabilities");
            }
        }
        
        return new HashMap<>();
    } catch (Exception e) {
        throw new RuntimeException("AI 분석 실패: " + e.getMessage());
    }
}
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
```

### 3. 서버 실행

```bash
python app.py
```

또는

```bash
flask run --host=0.0.0.0 --port=5002
```

### 4. Docker 실행

```bash
docker-compose up -d
```

## 테스트

### AI 모델 테스트

```bash
python test_ai_client.py
```

### API 문서

Swagger UI를 통해 API 문서를 확인할 수 있습니다:

```
http://172.16.29.250:5002/docs
```

## 프로젝트 구조

```
carrerAI_AI/
├── app.py                 # Flask 애플리케이션 메인 파일
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 설정
├── docker-compose.yml    # Docker Compose 설정
├── models/               # AI 모델 파일들
│   ├── xgb_model.pkl
│   └── label_map.pkl
├── config/               # 설정 파일
│   ├── __init__.py
│   └── settings.py
├── routes/               # API 라우트
│   ├── __init__.py
│   ├── pdf_routes.py
│   ├── prediction_routes.py
│   └── ai_routes.py
├── services/             # 비즈니스 로직
│   ├── __init__.py
│   ├── pdf_service.py
│   ├── prediction_service.py
│   ├── resume_parser_service.py
│   └── ai_model_service.py
├── utils/                # 유틸리티
│   ├── __init__.py
│   └── file_utils.py
├── test_client.py        # 기존 테스트 클라이언트
└── test_ai_client.py     # AI 모델 테스트 클라이언트
```

## 주의사항

1. **모델 파일**: `xgb_model.pkl`과 `label_map.pkl` 파일이 `models/` 디렉토리에 있어야 합니다.
2. **메모리 사용량**: AI 모델 로드 시 상당한 메모리를 사용할 수 있습니다.
3. **첫 요청 지연**: 첫 번째 분석 요청 시 모델 로드로 인한 지연이 발생할 수 있습니다.

## 라벨 매핑

### 학교 라벨
- 1.0: 서울대학교
- 2.0: 세종대학교
- 3.0: 연세대학교
- ...

### 전공 라벨
- 1.0: 경영학
- 2.0: 경제학
- 3.0: 문학
- 4.0: 공학
- 4.5: 컴퓨터/IT
- ...

### 어학점수 라벨
- 1: 하 (토익 600점 이하)
- 2: 중 (토익 800점)
- 3: 상 (토익 900점 이상) 
이 프로젝트는 MIT 라이센스 하에 배포됩니다. 