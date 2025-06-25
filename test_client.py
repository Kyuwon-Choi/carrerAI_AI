import requests
import json

# Flask 서비스 URL
BASE_URL = "http://localhost:5002"

def test_health_check():
    """헬스 체크 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("헬스 체크 결과:")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"헬스 체크 실패: {e}")

def test_text_to_pdf():
    """텍스트를 PDF로 변환하는 테스트"""
    try:
        # 테스트용 이력서 데이터
        resume_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "010-1234-5678",
            "address": "123 Main Street, Seoul, Korea",
            "education": [
                {
                    "school": "Seoul National University",
                    "period": "2018-2022",
                    "major": "Computer Science",
                    "degree": "Bachelor's Degree"
                },
                {
                    "school": "Seoul High School",
                    "period": "2015-2018",
                    "major": "Science",
                    "degree": "Graduation"
                }
            ],
            "experience": [
                {
                    "company": "Tech Solutions",
                    "period": "2022-2023",
                    "position": "Backend Developer",
                    "description": "Developed and maintained web applications using Spring Boot"
                },
                {
                    "company": "Startup XYZ",
                    "period": "2021-2022",
                    "position": "Intern Developer",
                    "description": "Developed web services using Python Django"
                }
            ],
            "skills": ["Java", "Spring Boot", "Python", "Django", "JavaScript", "React", "MySQL", "PostgreSQL"],
            "introduction": "Passionate developer who wants to create user-centered services. I love learning new technologies and value teamwork."
        }
        
        print("텍스트를 PDF로 변환 테스트:")
        print(f"전송할 데이터: {json.dumps(resume_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/text-to-pdf",
            json=resume_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            # PDF 파일 저장
            with open("test_resume_new.pdf", "wb") as f:
                f.write(response.content)
            print(f"PDF 생성 성공! 파일명: test_resume_new.pdf")
            print(f"파일 크기: {len(response.content)} bytes")
        else:
            print(f"PDF 생성 실패: {response.status_code}")
            print(f"에러 메시지: {response.text}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"텍스트를 PDF로 변환 테스트 실패: {e}")

def test_convert_resume_with_json():
    """통합 API로 JSON 데이터 전송 테스트"""
    try:
        resume_data = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "010-9876-5432",
            "address": "456 Oak Avenue, Busan, Korea",
            "education": [
                {
                    "school": "Busan National University",
                    "period": "2019-2023",
                    "major": "Software Engineering",
                    "degree": "Bachelor's Degree"
                }
            ],
            "experience": [
                {
                    "company": "IT Company",
                    "period": "2023-Present",
                    "position": "Frontend Developer",
                    "description": "Developed web applications using React and Vue.js"
                }
            ],
            "skills": ["JavaScript", "React", "Vue.js", "HTML", "CSS", "Node.js"],
            "introduction": "Frontend developer who values user experience."
        }
        
        print("통합 API JSON 테스트:")
        
        response = requests.post(
            f"{BASE_URL}/convert-resume",
            json=resume_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            with open("test_resume_integrated_new.pdf", "wb") as f:
                f.write(response.content)
            print(f"통합 API PDF 생성 성공! 파일명: test_resume_integrated_new.pdf")
        else:
            print(f"통합 API 실패: {response.status_code}")
            print(f"에러 메시지: {response.text}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"통합 API 테스트 실패: {e}")

def main():
    """모든 테스트 실행"""
    print("모듈화된 Flask 이력서 변환 서비스 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    test_health_check()
    
    # 2. 텍스트를 PDF로 변환
    test_text_to_pdf()
    
    # 3. 통합 API 테스트
    test_convert_resume_with_json()
    
    print("모든 테스트 완료!")

if __name__ == "__main__":
    main() 