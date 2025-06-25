import requests
import json

# Flask API URL
BASE_URL = "http://localhost:5002"

def test_ai_model_info():
    """AI 모델 정보 조회 테스트"""
    print("=== AI 모델 정보 조회 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ai/model/info")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 정보 조회 성공!")
            print(f"모델 로드 상태: {result.get('model_loaded')}")
            print(f"모델 타입: {result.get('model_type')}")
            print(f"기업 수: {result.get('companies_count')}")
            print(f"모델 경로: {result.get('model_path')}")
        else:
            print(f"❌ 모델 정보 조회 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_ai_model_load():
    """AI 모델 로드 테스트"""
    print("\n=== AI 모델 로드 ===")
    
    try:
        response = requests.post(f"{BASE_URL}/api/ai/model/load")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 로드 성공!")
            print(f"메시지: {result.get('message')}")
        else:
            print(f"❌ 모델 로드 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_ai_prediction():
    """AI 예측 테스트"""
    print("\n=== AI 예측 테스트 ===")
    
    # 테스트 데이터 (올바른 형식)
    test_data = {
        "user_id": 1,
        "recruitment_id": 101,
        "job_category": "백엔드",
        "age": 27,
        "school": 3,           # 4년제
        "major": 1,            # 컴퓨터공학
        "gpa": 3.7,
        "language_score": 850, # 토익
        "activity_score": 2,   # 대외활동
        "internship_score": 1, # 인턴
        "award_score": 1       # 수상
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/analyze-probability",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 예측 성공!")
            print(f"사용자 ID: {result.get('user_id')}")
            print(f"채용 ID: {result.get('recruitment_id')}")
            print(f"직무 카테고리: {result.get('job_category')}")
            print(f"예측 ID: {result.get('prediction_id')}")
            print(f"예측 시간: {result.get('prediction_time')}")
            
            # 기업별 확률 출력
            probabilities = result.get('probabilities', {})
            print("\n기업별 합격 확률:")
            for company, prob in probabilities.items():
                print(f"  - {company}: {prob}%")
                
        else:
            print(f"❌ 예측 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_multiple_predictions():
    """다양한 테스트 데이터로 예측"""
    print("\n=== 다양한 테스트 데이터 예측 ===")
    
    test_cases = [
        {
            "name": "신입 개발자",
            "data": {
                "user_id": 2,
                "recruitment_id": 102,
                "job_category": "프론트엔드",
                "age": 24,
                "school": 3,
                "major": 1,
                "gpa": 3.2,
                "language_score": 700,
                "activity_score": 0,
                "internship_score": 0,
                "award_score": 0
            }
        },
        {
            "name": "경력 개발자",
            "data": {
                "user_id": 3,
                "recruitment_id": 103,
                "job_category": "백엔드",
                "age": 29,
                "school": 4,
                "major": 1,
                "gpa": 4.1,
                "language_score": 920,
                "activity_score": 3,
                "internship_score": 2,
                "award_score": 2
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/analyze-probability",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                probabilities = result.get('probabilities', {})
                
                # 상위 3개 기업만 출력
                sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
                print("상위 3개 기업:")
                for company, prob in sorted_probs:
                    print(f"  - {company}: {prob}%")
            else:
                print(f"❌ 예측 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")

def main():
    """모든 AI API 테스트 실행"""
    print("🤖 AI API 테스트 시작")
    print("=" * 50)
    
    # 모델 정보 조회
    test_ai_model_info()
    
    # 모델 로드
    test_ai_model_load()
    
    # 단일 예측 테스트
    test_ai_prediction()
    
    # 다양한 예측 테스트
    test_multiple_predictions()
    
    print("\n" + "=" * 50)
    print("✅ AI API 테스트 완료!")

if __name__ == "__main__":
    main() 