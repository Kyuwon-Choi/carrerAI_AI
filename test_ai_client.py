import requests
import json

# Flask 서버 URL
FLASK_URL = "http://172.16.29.250:5002"

def test_ai_analysis():
    """AI 분석 엔드포인트 테스트"""
    
    # 테스트 데이터 (코랩에서 사용한 것과 동일)
    test_data = {
        "user_id": 1,
        "recruitment_id": 1,
        "job_category": "IT/개발",
        "age": 26,
        "school": 2.0,  # 세종대학교 라벨
        "major": 4.5,   # 컴퓨터/IT 라벨
        "gpa": 3.5,
        "language_score": 2,  # 중(토익 800점) 수준
        "activity_score": 12,
        "internship_score": 10,
        "award_score": 6
    }
    
    try:
        # AI 분석 요청
        print("AI 분석 요청 중...")
        response = requests.post(
            f"{FLASK_URL}/analyze-probability",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI 분석 성공!")
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 기업별 확률 출력
            if 'probabilities' in result:
                print("\n📊 기업별 확률:")
                for company, prob in result['probabilities'].items():
                    print(f"  {company}: {prob:.2f}%")
                    
        else:
            print(f"❌ AI 분석 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {str(e)}")

def test_model_info():
    """모델 정보 조회 테스트"""
    
    try:
        print("\n모델 정보 조회 중...")
        response = requests.get(f"{FLASK_URL}/api/ai/model/info")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 정보 조회 성공!")
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 모델 정보 조회 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {str(e)}")

def test_model_load():
    """모델 로드 테스트"""
    
    try:
        print("\n모델 로드 중...")
        response = requests.post(f"{FLASK_URL}/api/ai/model/load")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 로드 성공!")
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 모델 로드 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 AI 모델 테스트 시작")
    print(f"Flask 서버 URL: {FLASK_URL}")
    
    # 모델 정보 조회
    test_model_info()
    
    # 모델 로드
    test_model_load()
    
    # AI 분석 테스트
    test_ai_analysis()
    
    print("\n✨ 테스트 완료!") 