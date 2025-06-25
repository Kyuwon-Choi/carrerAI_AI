import requests
import json
import os
from datetime import datetime

# Flask 서비스 URL
BASE_URL = "http://localhost:5002"

class CareerAITestClient:
    """CareerAI 백엔드 테스트 클라이언트"""
    
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_pdf_conversion(self):
        """PDF 변환 API 테스트"""
        print("\n=== PDF 변환 API 테스트 ===")
        
        # 테스트용 JSON 데이터
        test_data = {
            "name": "홍길동",
            "age": 28,
            "experience": 3.5,
            "skills": ["Python", "Flask", "React", "Docker"],
            "education": "컴퓨터공학과 졸업",
            "etc": "프로젝트 경험 다수"
        }
        
        try:
            # JSON 데이터로 PDF 생성
            response = self.session.post(
                f"{self.base_url}/api/documents/",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                # PDF 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_resume_{timestamp}.pdf"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ PDF 변환 성공: {filename}")
                print(f"   파일 크기: {len(response.content)} bytes")
            else:
                print(f"❌ PDF 변환 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ PDF 변환 테스트 오류: {str(e)}")
    
    def test_prediction_api(self):
        """예측 API 테스트"""
        print("\n=== 기업 확률 예측 API 테스트 ===")
        
        # 테스트용 사용자 데이터
        test_users = [
            {
                "name": "김개발",
                "age": 25,
                "experience": 2.0,
                "skills": ["Java", "Spring", "MySQL"],
                "education": "정보통신공학과 졸업",
                "etc": "스타트업 경험 1년"
            },
            {
                "name": "이시니어",
                "age": 32,
                "experience": 8.0,
                "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
                "education": "컴퓨터공학과 석사",
                "etc": "대기업 경력 5년, 스타트업 CTO 경험"
            },
            {
                "name": "박주니어",
                "age": 23,
                "experience": 0.5,
                "skills": ["JavaScript", "React"],
                "education": "컴퓨터공학과 재학",
                "etc": "인턴 경험 6개월"
            }
        ]
        
        prediction_ids = []
        
        for i, user_data in enumerate(test_users, 1):
            print(f"\n--- 테스트 케이스 {i}: {user_data['name']} ---")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/predictions/",
                    json=user_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    result = response.json()
                    prediction_ids.append(result['id'])
                    print(f"✅ 예측 성공 (ID: {result['id']})")
                    print(f"   기업 확률: {result['probability']:.2%}")
                    print(f"   신뢰도: {result['confidence']:.2%}")
                    print(f"   상태: {result['status']}")
                    print(f"   생성 시간: {result['created_at']}")
                    print(f"   추천사항:")
                    for rec in result['recommendations']:
                        print(f"     - {rec}")
                else:
                    print(f"❌ 예측 실패: {response.status_code}")
                    print(f"   응답: {response.text}")
                    
            except Exception as e:
                print(f"❌ 예측 테스트 오류: {str(e)}")
        
        # 예측 결과 조회 테스트
        if prediction_ids:
            print(f"\n--- 예측 결과 조회 테스트 ---")
            for pred_id in prediction_ids[:1]:  # 첫 번째 예측만 테스트
                try:
                    response = self.session.get(f"{self.base_url}/api/predictions/{pred_id}")
                    if response.status_code == 200:
                        print(f"✅ 예측 조회 성공: {pred_id}")
                    else:
                        print(f"❌ 예측 조회 실패: {response.status_code}")
                except Exception as e:
                    print(f"❌ 예측 조회 오류: {str(e)}")
    
    def test_model_info(self):
        """모델 정보 조회 테스트"""
        print("\n=== 모델 정보 조회 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/predictions/model")
            
            if response.status_code == 200:
                info = response.json()
                print("✅ 모델 정보 조회 성공")
                print(f"   모델 로드 상태: {info['model_loaded']}")
                print(f"   모델 경로: {info['model_path']}")
                print(f"   모델 타입: {info['model_type']}")
                print(f"   버전: {info['version']}")
                print(f"   마지막 업데이트: {info['last_updated']}")
            else:
                print(f"❌ 모델 정보 조회 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 모델 정보 조회 오류: {str(e)}")
    
    def test_model_load(self):
        """모델 로드 테스트"""
        print("\n=== 모델 로드 테스트 ===")
        
        try:
            # 모델 로드 요청
            response = self.session.post(f"{self.base_url}/api/predictions/model")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 모델 로드 성공: {result['message']}")
                if 'model_name' in result:
                    print(f"   모델명: {result['model_name']}")
            else:
                print(f"❌ 모델 로드 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 모델 로드 테스트 오류: {str(e)}")
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        print("\n=== 헬스 체크 테스트 ===")
        
        # 예측 서비스 헬스 체크
        try:
            response = self.session.get(f"{self.base_url}/api/predictions/health")
            
            if response.status_code == 200:
                health = response.json()
                print("✅ 예측 서비스 헬스 체크 성공")
                print(f"   상태: {health['status']}")
                print(f"   모델 로드: {health['model_loaded']}")
                print(f"   서비스: {health['service']}")
                print(f"   시간: {health['timestamp']}")
            else:
                print(f"❌ 예측 서비스 헬스 체크 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 예측 서비스 헬스 체크 오류: {str(e)}")
        
        # PDF 서비스 헬스 체크
        try:
            response = self.session.get(f"{self.base_url}/api/documents/health")
            
            if response.status_code == 200:
                health = response.json()
                print("✅ PDF 서비스 헬스 체크 성공")
                print(f"   상태: {health['status']}")
                print(f"   서비스: {health['service']}")
                print(f"   시간: {health['timestamp']}")
            else:
                print(f"❌ PDF 서비스 헬스 체크 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ PDF 서비스 헬스 체크 오류: {str(e)}")
    
    def test_swagger_docs(self):
        """Swagger 문서 접근 테스트"""
        print("\n=== Swagger 문서 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/docs")
            
            if response.status_code == 200:
                print("✅ Swagger 문서 접근 성공")
                print(f"   문서 크기: {len(response.text)} bytes")
            else:
                print(f"❌ Swagger 문서 접근 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Swagger 문서 테스트 오류: {str(e)}")
    
    def test_api_structure(self):
        """API 구조 테스트"""
        print("\n=== API 구조 테스트 ===")
        
        # 예측 목록 조회
        try:
            response = self.session.get(f"{self.base_url}/api/predictions/")
            if response.status_code == 200:
                result = response.json()
                print("✅ 예측 목록 조회 성공")
                print(f"   총 예측 수: {result['total']}")
                print(f"   현재 페이지: {result['page']}")
            else:
                print(f"❌ 예측 목록 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 예측 목록 조회 오류: {str(e)}")
        
        # 문서 목록 조회
        try:
            response = self.session.get(f"{self.base_url}/api/documents/")
            if response.status_code == 200:
                result = response.json()
                print("✅ 문서 목록 조회 성공")
                print(f"   총 문서 수: {result['total']}")
                print(f"   현재 페이지: {result['page']}")
            else:
                print(f"❌ 문서 목록 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 문서 목록 조회 오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 CareerAI 백엔드 테스트 시작")
        print(f"   서버 URL: {self.base_url}")
        print(f"   테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 서버 연결 테스트
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ 서버 연결 성공")
            else:
                print(f"⚠️  서버 응답: {response.status_code}")
        except Exception as e:
            print(f"❌ 서버 연결 실패: {str(e)}")
            return
        
        # 각종 테스트 실행
        self.test_health_check()
        self.test_model_info()
        self.test_model_load()
        self.test_prediction_api()
        self.test_pdf_conversion()
        self.test_api_structure()
        self.test_swagger_docs()
        
        print("\n🎉 모든 테스트 완료!")

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
            with open("test_resume.pdf", "wb") as f:
                f.write(response.content)
            print(f"PDF 생성 성공! 파일명: test_resume.pdf")
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
            with open("test_resume_integrated.pdf", "wb") as f:
                f.write(response.content)
            print(f"통합 API PDF 생성 성공! 파일명: test_resume_integrated.pdf")
        else:
            print(f"통합 API 실패: {response.status_code}")
            print(f"에러 메시지: {response.text}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"통합 API 테스트 실패: {e}")

def test_content_type_validation():
    """Content-Type 검증 테스트"""
    try:
        print("Content-Type 검증 테스트:")
        
        # 잘못된 Content-Type으로 JSON 엔드포인트 호출
        response = requests.post(
            f"{BASE_URL}/text-to-pdf",
            data="invalid data",
            headers={'Content-Type': 'text/plain'}
        )
        print(f"잘못된 Content-Type 테스트: {response.status_code} - {response.json()}")
        
        # 잘못된 Content-Type으로 파일 업로드 엔드포인트 호출
        response = requests.post(
            f"{BASE_URL}/pdf-to-text",
            data="invalid data",
            headers={'Content-Type': 'text/plain'}
        )
        print(f"잘못된 Content-Type 테스트: {response.status_code} - {response.json()}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"Content-Type 검증 테스트 실패: {e}")

def test_pdf_text_extraction():
    """PDF 텍스트 추출 테스트"""
    print("=== PDF 텍스트 추출 테스트 ===")
    
    # 테스트용 PDF 파일 경로 (실제 파일이 있어야 함)
    pdf_file_path = "test_resume.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"테스트 파일이 없습니다: {pdf_file_path}")
        return
    
    try:
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents/convert", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 텍스트 추출 성공!")
            print(f"문서 ID: {result.get('id')}")
            print(f"상태: {result.get('status')}")
            print(f"텍스트 길이: {len(result.get('content', ''))}")
            print(f"텍스트 미리보기: {result.get('content', '')[:200]}...")
        else:
            print(f"❌ 텍스트 추출 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_resume_parsing():
    """이력서 파싱 테스트"""
    print("\n=== 이력서 파싱 테스트 ===")
    
    # 테스트용 PDF 파일 경로 (실제 파일이 있어야 함)
    pdf_file_path = "test_resume.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"테스트 파일이 없습니다: {pdf_file_path}")
        return
    
    try:
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents/parse-resume", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 이력서 파싱 성공!")
            print(f"문서 ID: {result.get('id')}")
            print(f"상태: {result.get('status')}")
            
            parsed_data = result.get('parsed_data', {})
            print(f"📱 핸드폰: {parsed_data.get('phone', 'N/A')}")
            print(f"📧 이메일: {parsed_data.get('email', 'N/A')}")
            print(f"💼 경력 수: {len(parsed_data.get('experiences', []))}")
            print(f"🛠️ 스킬 수: {len(parsed_data.get('skills', []))}")
            print(f"🔗 링크 수: {len(parsed_data.get('links', []))}")
            print(f"🏆 수상 수: {len(parsed_data.get('awards', []))}")
            print(f"📜 자격증 수: {len(parsed_data.get('certificates', []))}")
            print(f"🌍 어학 수: {len(parsed_data.get('languages', []))}")
            print(f"💻 프로젝트 수: {len(parsed_data.get('projects', []))}")
            
            # 상세 정보 출력
            if parsed_data.get('experiences'):
                print("\n📋 경력 정보:")
                for exp in parsed_data['experiences']:
                    print(f"  - {exp.get('company')} ({exp.get('start_date')} ~ {exp.get('end_date')})")
                    print(f"    직책: {exp.get('position')}")
            
            if parsed_data.get('skills'):
                print("\n🛠️ 스킬 정보:")
                for skill in parsed_data['skills']:
                    print(f"  - {skill.get('name')}")
            
        else:
            print(f"❌ 이력서 파싱 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_legacy_endpoints():
    """기존 URL 엔드포인트 테스트"""
    print("\n=== 기존 URL 호환성 테스트 ===")
    
    # 테스트용 PDF 파일 경로
    pdf_file_path = "test_resume.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"테스트 파일이 없습니다: {pdf_file_path}")
        return
    
    try:
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            
            # 기존 URL로 텍스트 추출 테스트
            response = requests.post(f"{BASE_URL}/documents/convert", files=files)
            if response.status_code == 200:
                print("✅ 기존 URL 텍스트 추출 성공!")
            else:
                print(f"❌ 기존 URL 텍스트 추출 실패: {response.status_code}")
            
            # 기존 URL로 이력서 파싱 테스트
            f.seek(0)  # 파일 포인터 리셋
            response = requests.post(f"{BASE_URL}/documents/parse-resume", files=files)
            if response.status_code == 200:
                print("✅ 기존 URL 이력서 파싱 성공!")
            else:
                print(f"❌ 기존 URL 이력서 파싱 실패: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_prediction_api():
    """예측 API 테스트"""
    print("\n=== 기업 확률 예측 테스트 ===")
    
    # 테스트 데이터
    test_data = {
        "resume_data": {
            "phone": "010-1234-5678",
            "email": "test@example.com",
            "introduction": "열정적인 개발자입니다.",
            "experiences": [
                {
                    "company": "네이버",
                    "start_date": "2021.03",
                    "end_date": "2023.05",
                    "position": "백엔드 개발자",
                    "description": "Spring Boot를 사용한 웹 서비스 개발"
                }
            ],
            "skills": [
                {"name": "Spring Boot", "level": "상"},
                {"name": "Java", "level": "상"},
                {"name": "MySQL", "level": "중"}
            ],
            "links": [
                {"type": "github", "url": "https://github.com/test"},
                {"type": "blog", "url": "https://blog.test.com"}
            ],
            "awards": [],
            "certificates": [],
            "languages": [],
            "projects": []
        },
        "company_name": "카카오"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predictions/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 예측 성공!")
            print(f"기업: {result.get('company_name')}")
            print(f"확률: {result.get('probability')}%")
            print(f"예측 ID: {result.get('prediction_id')}")
        else:
            print(f"❌ 예측 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_health_check():
    """헬스 체크 테스트"""
    print("\n=== 헬스 체크 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/documents/health")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 서비스 정상!")
            print(f"상태: {result.get('status')}")
            print(f"서비스: {result.get('service')}")
            print(f"시간: {result.get('timestamp')}")
        else:
            print(f"❌ 서비스 오류: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_api_info():
    """API 정보 테스트"""
    print("\n=== API 정보 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 정보 조회 성공!")
            print(f"메시지: {result.get('message')}")
            print(f"버전: {result.get('version')}")
            print("엔드포인트:")
            for key, value in result.get('endpoints', {}).items():
                print(f"  - {key}: {value}")
        else:
            print(f"❌ API 정보 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def main():
    """모든 테스트 실행"""
    print("🚀 CareerAI API 테스트 시작")
    print("=" * 50)
    
    # API 정보 확인
    test_api_info()
    
    # 헬스 체크
    test_health_check()
    
    # PDF 텍스트 추출 테스트
    test_pdf_text_extraction()
    
    # 이력서 파싱 테스트
    test_resume_parsing()
    
    # 기존 URL 호환성 테스트
    test_legacy_endpoints()
    
    # 예측 API 테스트
    test_prediction_api()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")

if __name__ == "__main__":
    main() 