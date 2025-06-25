from flask import request, send_file
from flask_restx import Namespace, Resource, fields, reqparse
import tempfile
import os
import io
from services.pdf_service import PDFService
from services.resume_parser_service import ResumeParserService
from utils.file_utils import allowed_file, ensure_upload_folder
from config.settings import Config

# PDF 관련 API 네임스페이스 생성
api = Namespace('documents', description='PDF 문서 변환 API')

# Swagger 모델 정의
resume_model = api.model('Resume', {
    'name': fields.String(required=True, description='이름'),
    'age': fields.Integer(required=True, description='나이'),
    'experience': fields.Float(required=True, description='경력 (년)'),
    'skills': fields.List(fields.String, required=True, description='기술 스택'),
    'education': fields.String(description='학력'),
    'etc': fields.String(description='기타 정보')
})

# 이력서 파싱 결과 모델
experience_model = api.model('Experience', {
    'company': fields.String(description='회사명'),
    'start_date': fields.String(description='시작일'),
    'end_date': fields.String(description='종료일'),
    'position': fields.String(description='직책'),
    'description': fields.String(description='업무 설명')
})

skill_model = api.model('Skill', {
    'name': fields.String(description='기술명'),
    'level': fields.String(description='숙련도')
})

link_model = api.model('Link', {
    'type': fields.String(description='링크 타입 (blog, github 등)'),
    'url': fields.String(description='URL')
})

award_model = api.model('Award', {
    'title': fields.String(description='수상명'),
    'date': fields.String(description='수상일'),
    'organization': fields.String(description='수여기관')
})

certificate_model = api.model('Certificate', {
    'name': fields.String(description='자격증명'),
    'date': fields.String(description='취득일'),
    'organization': fields.String(description='발급기관')
})

language_model = api.model('Language', {
    'name': fields.String(description='언어명'),
    'level': fields.String(description='수준')
})

project_model = api.model('Project', {
    'name': fields.String(description='프로젝트명'),
    'period': fields.String(description='기간'),
    'description': fields.String(description='프로젝트 설명'),
    'technologies': fields.List(fields.String, description='사용 기술')
})

parsed_resume_model = api.model('ParsedResume', {
    'phone': fields.String(description='핸드폰 번호'),
    'email': fields.String(description='이메일'),
    'introduction': fields.String(description='간단 자기소개'),
    'experiences': fields.List(fields.Nested(experience_model), description='경력 목록'),
    'skills': fields.List(fields.Nested(skill_model), description='스킬 목록'),
    'links': fields.List(fields.Nested(link_model), description='링크 목록'),
    'awards': fields.List(fields.Nested(award_model), description='수상 목록'),
    'certificates': fields.List(fields.Nested(certificate_model), description='자격증 목록'),
    'languages': fields.List(fields.Nested(language_model), description='어학 목록'),
    'projects': fields.List(fields.Nested(project_model), description='프로젝트 경험 목록')
})

document_response_model = api.model('DocumentResponse', {
    'id': fields.String(description='문서 ID'),
    'type': fields.String(description='문서 타입 (pdf/text)'),
    'content': fields.String(description='문서 내용 (텍스트 추출 시)'),
    'file_size': fields.Integer(description='파일 크기 (bytes)'),
    'created_at': fields.String(description='생성 시간'),
    'status': fields.String(description='상태')
})

document_list_model = api.model('DocumentList', {
    'documents': fields.List(fields.Nested(document_response_model), description='문서 목록'),
    'total': fields.Integer(description='총 문서 수'),
    'page': fields.Integer(description='현재 페이지'),
    'per_page': fields.Integer(description='페이지당 항목 수')
})

error_model = api.model('Error', {
    'error': fields.String(description='오류 메시지'),
    'code': fields.String(description='오류 코드'),
    'details': fields.String(description='상세 정보')
})

# 파일 업로드를 위한 RequestParser (Swagger 문서화용)
file_upload_parser = reqparse.RequestParser()
file_upload_parser.add_argument('file', location='files', type='FileStorage', required=True, help='PDF 파일')

def extract_text_from_pdf_file(file):
    """PDF 파일에서 텍스트를 추출하는 공통 함수"""
    if not file:
        return {
            'error': '파일이 없습니다.',
            'code': 'MISSING_FILE',
            'details': 'PDF 파일을 선택해주세요.'
        }, 400
    
    if file.filename == '':
        return {
            'error': '선택된 파일이 없습니다.',
            'code': 'EMPTY_FILE',
            'details': '유효한 PDF 파일을 선택해주세요.'
        }, 400
    
    if not allowed_file(file.filename):
        return {
            'error': 'PDF 파일만 업로드 가능합니다.',
            'code': 'INVALID_FILE_TYPE',
            'details': 'PDF 형식의 파일만 지원합니다.'
        }, 400
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name
    
    try:
        print(f"PDF 파일 저장됨: {temp_file_path}")
        print(f"파일 크기: {os.path.getsize(temp_file_path)} bytes")
        
        # PDF에서 텍스트 추출
        extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
        
        print(f"추출된 텍스트 길이: {len(extracted_text) if extracted_text else 0}")
        print(f"추출된 텍스트 미리보기: {extracted_text[:200] if extracted_text else 'None'}")
        
        from datetime import datetime
        import uuid
        
        response_data = {
            'id': str(uuid.uuid4()),
            'type': 'text',
            'content': extracted_text,
            'file_size': len(extracted_text.encode('utf-8')) if extracted_text else 0,
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        print(f"응답 데이터: {response_data}")
        return response_data
        
    except Exception as e:
        print(f"텍스트 추출 중 오류: {str(e)}")
        return {
            'error': '텍스트 추출 중 오류가 발생했습니다.',
            'code': 'TEXT_EXTRACTION_ERROR',
            'details': str(e)
        }, 500
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"임시 파일 삭제됨: {temp_file_path}")

def parse_resume_from_pdf_file(file):
    """PDF 파일에서 이력서 정보를 파싱하는 함수"""
    if not file:
        return {
            'error': '파일이 없습니다.',
            'code': 'MISSING_FILE',
            'details': 'PDF 파일을 선택해주세요.'
        }, 400
    
    if file.filename == '':
        return {
            'error': '선택된 파일이 없습니다.',
            'code': 'EMPTY_FILE',
            'details': '유효한 PDF 파일을 선택해주세요.'
        }, 400
    
    if not allowed_file(file.filename):
        return {
            'error': 'PDF 파일만 업로드 가능합니다.',
            'code': 'INVALID_FILE_TYPE',
            'details': 'PDF 형식의 파일만 지원합니다.'
        }, 400
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name
    
    try:
        print(f"이력서 PDF 파일 저장됨: {temp_file_path}")
        
        # PDF에서 텍스트 추출
        extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
        
        if not extracted_text:
            return {
                'error': 'PDF에서 텍스트를 추출할 수 없습니다.',
                'code': 'NO_TEXT_EXTRACTED',
                'details': 'PDF 파일이 텍스트를 포함하지 않거나 이미지로만 구성되어 있습니다.'
            }, 400
        
        print(f"추출된 텍스트 길이: {len(extracted_text)}")
        
        # 이력서 정보 파싱
        parsed_resume = ResumeParserService.parse_resume(extracted_text)
        
        from datetime import datetime
        import uuid
        
        response_data = {
            'id': str(uuid.uuid4()),
            'type': 'parsed_resume',
            'parsed_data': parsed_resume,
            'raw_text': extracted_text,
            'file_size': len(extracted_text.encode('utf-8')),
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        print(f"파싱된 이력서 데이터: {parsed_resume}")
        return response_data
        
    except Exception as e:
        print(f"이력서 파싱 중 오류: {str(e)}")
        return {
            'error': '이력서 파싱 중 오류가 발생했습니다.',
            'code': 'RESUME_PARSING_ERROR',
            'details': str(e)
        }, 500
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"임시 파일 삭제됨: {temp_file_path}")

@api.route('/')
class DocumentListResource(Resource):
    """문서 목록 및 새 문서 생성"""
    
    @api.doc('문서 목록 조회')
    @api.response(200, '조회 성공', document_list_model)
    def get(self):
        """
        문서 목록을 조회합니다.
        
        쿼리 파라미터:
        - page: 페이지 번호 (기본값: 1)
        - per_page: 페이지당 항목 수 (기본값: 10)
        - type: 문서 타입 필터 (pdf/text)
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            doc_type = request.args.get('type')
            
            # TODO: 실제 문서 목록 구현
            # 현재는 더미 데이터 반환
            documents = []
            
            return {
                'documents': documents,
                'total': len(documents),
                'page': page,
                'per_page': per_page
            }, 200
            
        except Exception as e:
            return {
                'error': '문서 목록 조회 중 오류가 발생했습니다.',
                'code': 'DOCUMENT_LIST_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('새 문서 생성 (PDF 변환)')
    @api.expect(resume_model)
    @api.response(201, '문서 생성 성공')
    @api.response(400, '잘못된 요청', error_model)
    @api.response(500, '서버 오류', error_model)
    def post(self):
        """
        새로운 PDF 문서를 생성합니다.
        
        입력 데이터:
        - name: 이름 (필수)
        - age: 나이 (필수, 18-100)
        - experience: 경력 (필수, 년 단위)
        - skills: 기술 스택 (필수, 리스트)
        - education: 학력 (선택)
        - etc: 기타 정보 (선택)
        
        반환: PDF 파일 (binary)
        """
        try:
            # application/json 확인
            if 'application/json' not in request.headers.get('Content-Type', ''):
                return {
                    'error': 'Content-Type이 application/json이어야 합니다.',
                    'code': 'INVALID_CONTENT_TYPE',
                    'details': 'JSON 데이터를 제공해주세요.'
                }, 400
            
            data = request.get_json()
            
            if not data:
                return {
                    'error': 'JSON 데이터가 없습니다.',
                    'code': 'MISSING_DATA',
                    'details': '이력서 데이터를 제공해주세요.'
                }, 400
            
            # PDF 생성
            pdf_content = PDFService.create_pdf_from_data(data)
            
            # PDF 파일로 응답
            return send_file(
                io.BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='resume.pdf'
            )
            
        except Exception as e:
            return {
                'error': 'PDF 생성 중 오류가 발생했습니다.',
                'code': 'PDF_GENERATION_ERROR',
                'details': str(e)
            }, 500

@api.route('/<string:document_id>')
class DocumentResource(Resource):
    """특정 문서 조회, 수정, 삭제"""
    
    @api.doc('특정 문서 조회')
    @api.response(200, '조회 성공')
    @api.response(404, '문서를 찾을 수 없음', error_model)
    def get(self, document_id):
        """
        특정 문서를 조회합니다.
        
        파라미터:
        - document_id: 문서 ID
        """
        try:
            # TODO: 실제 문서 조회 구현
            return {
                'error': '문서를 찾을 수 없습니다.',
                'code': 'DOCUMENT_NOT_FOUND',
                'details': f'ID {document_id}에 해당하는 문서가 없습니다.'
            }, 404
            
        except Exception as e:
            return {
                'error': '문서 조회 중 오류가 발생했습니다.',
                'code': 'DOCUMENT_GET_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('문서 수정')
    @api.expect(resume_model)
    @api.response(200, '수정 성공')
    @api.response(404, '문서를 찾을 수 없음', error_model)
    def put(self, document_id):
        """
        특정 문서를 수정합니다.
        
        파라미터:
        - document_id: 문서 ID
        """
        try:
            # TODO: 실제 문서 수정 구현
            return {
                'error': '문서를 찾을 수 없습니다.',
                'code': 'DOCUMENT_NOT_FOUND',
                'details': f'ID {document_id}에 해당하는 문서가 없습니다.'
            }, 404
            
        except Exception as e:
            return {
                'error': '문서 수정 중 오류가 발생했습니다.',
                'code': 'DOCUMENT_UPDATE_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('문서 삭제')
    @api.response(204, '삭제 성공')
    @api.response(404, '문서를 찾을 수 없음', error_model)
    def delete(self, document_id):
        """
        특정 문서를 삭제합니다.
        
        파라미터:
        - document_id: 문서 ID
        """
        try:
            # TODO: 실제 문서 삭제 구현
            return '', 204
            
        except Exception as e:
            return {
                'error': '문서 삭제 중 오류가 발생했습니다.',
                'code': 'DOCUMENT_DELETE_ERROR',
                'details': str(e)
            }, 500

@api.route('/convert')
class DocumentConvertResource(Resource):
    """문서 변환 (PDF ↔ 텍스트)"""
    
    @api.doc('PDF 텍스트 추출')
    @api.expect(file_upload_parser)
    @api.response(200, '텍스트 추출 성공', document_response_model)
    @api.response(400, '잘못된 요청', error_model)
    @api.response(500, '서버 오류', error_model)
    def post(self):
        """
        PDF 파일을 텍스트로 변환합니다.
        
        요청: multipart/form-data
        - file: PDF 파일
        
        반환: 추출된 텍스트
        """
        try:
            # multipart/form-data 확인
            if 'multipart/form-data' not in request.headers.get('Content-Type', ''):
                return {
                    'error': 'Content-Type이 multipart/form-data여야 합니다.',
                    'code': 'INVALID_CONTENT_TYPE',
                    'details': 'PDF 파일을 업로드해주세요.'
                }, 400
            
            if 'file' not in request.files:
                return {
                    'error': '파일이 없습니다.',
                    'code': 'MISSING_FILE',
                    'details': 'PDF 파일을 선택해주세요.'
                }, 400
            
            file = request.files['file']
            result = extract_text_from_pdf_file(file)
            
            if isinstance(result, tuple):
                return result  # 오류 응답
            else:
                return result  # 성공 응답
                    
        except Exception as e:
            return {
                'error': '텍스트 추출 중 오류가 발생했습니다.',
                'code': 'TEXT_EXTRACTION_ERROR',
                'details': str(e)
            }, 500

@api.route('/parse-resume')
class ResumeParseResource(Resource):
    """이력서 PDF 파싱"""
    
    @api.doc('이력서 PDF 파싱')
    @api.expect(file_upload_parser)
    @api.response(200, '이력서 파싱 성공')
    @api.response(400, '잘못된 요청', error_model)
    @api.response(500, '서버 오류', error_model)
    def post(self):
        """
        PDF 이력서를 구조화된 데이터로 파싱합니다.
        
        요청: multipart/form-data
        - file: PDF 이력서 파일
        
        반환: 파싱된 이력서 데이터
        - phone: 핸드폰 번호
        - email: 이메일
        - introduction: 간단 자기소개
        - experiences: 경력 목록
        - skills: 스킬 목록
        - links: 링크 목록
        - awards: 수상 목록
        - certificates: 자격증 목록
        - languages: 어학 목록
        - projects: 프로젝트 경험 목록
        """
        try:
            # multipart/form-data 확인
            if 'multipart/form-data' not in request.headers.get('Content-Type', ''):
                return {
                    'error': 'Content-Type이 multipart/form-data여야 합니다.',
                    'code': 'INVALID_CONTENT_TYPE',
                    'details': 'PDF 파일을 업로드해주세요.'
                }, 400
            
            if 'file' not in request.files:
                return {
                    'error': '파일이 없습니다.',
                    'code': 'MISSING_FILE',
                    'details': 'PDF 파일을 선택해주세요.'
                }, 400
            
            file = request.files['file']
            result = parse_resume_from_pdf_file(file)
            
            if isinstance(result, tuple):
                return result  # 오류 응답
            else:
                return result  # 성공 응답
                    
        except Exception as e:
            return {
                'error': '이력서 파싱 중 오류가 발생했습니다.',
                'code': 'RESUME_PARSING_ERROR',
                'details': str(e)
            }, 500

@api.route('/health')
class HealthResource(Resource):
    """서비스 상태 확인"""
    
    @api.doc('헬스 체크')
    @api.response(200, '서비스 정상')
    def get(self):
        """
        PDF 서비스의 상태를 확인합니다.
        
        반환 데이터:
        - status: 서비스 상태
        - service: 서비스명
        - timestamp: 확인 시간
        """
        try:
            from datetime import datetime
            
            return {
                'status': 'healthy',
                'service': 'pdf_service',
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'service': 'pdf_service',
                'timestamp': datetime.now().isoformat()
            }, 500 