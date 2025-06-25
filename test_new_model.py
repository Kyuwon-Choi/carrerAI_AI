import requests
import json

# Flask API URL
BASE_URL = "http://localhost:5002"

def test_new_model():
    """새로운 유사도 점수 모델 테스트"""
    print("🔄 새로운 유사도 점수 모델 테스트")
    print("=" * 60)
    
    # 테스트 데이터 (세종대 학생 데이터)
    test_data = {
        "user_id": 1,
        "recruitment_id": 101,
        "job_category": "백엔드",
        "age": 26,
        "school": 2.0,  # 세종대학교
        "major": 4.5,   # 컴퓨터/IT
        "gpa": 3.5,
        "language_score": 2,
        "activity_score": 12,
        "internship_score": 10,
        "award_score": 6
    }
    
    try:
        # 모델 로드
        print("1️⃣ AI 모델 로드 중...")
        response = requests.post(f"{BASE_URL}/api/ai/model/load")
        
        if response.status_code != 200:
            print(f"❌ 모델 로드 실패: {response.status_code}")
            return
        
        print("✅ 모델 로드 성공!")
        
        # 예측 수행
        print("\n2️⃣ 예측 수행 중...")
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
            print(f"\n🎯 기업별 합격 확률 (유사도 점수 반영):")
            print("-" * 50)
            
            for i, (company, prob) in enumerate(probabilities.items(), 1):
                print(f"{i:2d}. {company:<12} : {prob:>6.2f}%")
            
            # 상위 3개 기업 강조
            top_3 = list(probabilities.items())[:3]
            print(f"\n🏆 상위 3개 기업:")
            for i, (company, prob) in enumerate(top_3, 1):
                print(f"   {i}. {company} ({prob:.2f}%)")
                
        else:
            print(f"❌ 예측 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_multiple_scenarios():
    """다양한 시나리오 테스트"""
    print("\n" + "=" * 60)
    print("🔄 다양한 시나리오 테스트")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "세종대 우수 학생",
            "data": {
                "user_id": 2,
                "recruitment_id": 102,
                "job_category": "프론트엔드",
                "age": 24,
                "school": 2.0,  # 세종대
                "major": 4.5,   # 컴퓨터/IT
                "gpa": 4.1,
                "language_score": 3,
                "activity_score": 15,
                "internship_score": 12,
                "award_score": 8
            }
        },
        {
            "name": "다른 대학 학생",
            "data": {
                "user_id": 3,
                "recruitment_id": 103,
                "job_category": "백엔드",
                "age": 25,
                "school": 3.0,  # 다른 대학
                "major": 4.5,   # 컴퓨터/IT
                "gpa": 3.8,
                "language_score": 2,
                "activity_score": 10,
                "internship_score": 8,
                "award_score": 5
            }
        },
        {
            "name": "신입 개발자",
            "data": {
                "user_id": 4,
                "recruitment_id": 104,
                "job_category": "풀스택",
                "age": 23,
                "school": 2.0,  # 세종대
                "major": 4.5,   # 컴퓨터/IT
                "gpa": 3.2,
                "language_score": 1,
                "activity_score": 5,
                "internship_score": 2,
                "award_score": 1
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/analyze-probability",
                json=scenario['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                probabilities = result.get('probabilities', {})
                
                # 상위 3개 기업만 출력
                top_3 = list(probabilities.items())[:3]
                for i, (company, prob) in enumerate(top_3, 1):
                    print(f"   {i}. {company:<12} : {prob:>6.2f}%")
            else:
                print(f"   ❌ 예측 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")

def test_model_info():
    """모델 정보 조회"""
    print("\n" + "=" * 60)
    print("ℹ️ 모델 정보 조회")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/ai/model/info")
        
        if response.status_code == 200:
            info = response.json()
            print(f"모델 타입: {info.get('model_type')}")
            print(f"버전: {info.get('version')}")
            print(f"모델 로드 상태: {info.get('model_loaded')}")
            print(f"기업 수: {info.get('companies_count')}")
            
            print(f"\n사후 가중치 (세종대 우대):")
            post_weights = info.get('post_weights', {})
            for company, weight in post_weights.items():
                print(f"  - {company}: {weight}")
            
            print(f"\n유사도 점수:")
            similarity_scores = info.get('similarity_scores', {})
            for company, score in similarity_scores.items():
                print(f"  - {company}: {score}")
                
        else:
            print(f"❌ 모델 정보 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def main():
    """메인 테스트 함수"""
    print("🚀 새로운 유사도 점수 모델 테스트 시작")
    
    # 모델 정보 조회
    test_model_info()
    
    # 새로운 모델 테스트
    test_new_model()
    
    # 다양한 시나리오 테스트
    test_multiple_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")

if __name__ == "__main__":
    main() 