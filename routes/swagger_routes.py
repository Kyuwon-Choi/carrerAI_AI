from flask import Blueprint
from flask_restx import Api, Resource, fields, Namespace
from flask import request, jsonify, send_file
import tempfile
import os
import io
from services.pdf_service import PDFService
from utils.file_utils import allowed_file, ensure_upload_folder
from config.settings import Config

# Swagger UI를 위한 블루프린트 생성
swagger_bp = Blueprint('swagger', __name__)

# API 네임스페이스 생성
api = Api(swagger_bp, 
    title='이력서 PDF 변환 API',
    version='1.0',
    description='Spring 백엔드와 통신하는 Flask 기반 이력서 PDF 변환 서비스 API',
    doc='/docs'
)

# 네임스페이스 생성
health_ns = Namespace('health', description='헬스 체크 관련 API')
pdf_ns = Namespace('pdf', description='PDF 변환 관련 API')

api.add_namespace(health_ns)
api.add_namespace(pdf_ns)

# 모델 정의
resume_model = api.model('Resume', {
    'name': fields.String(required=True, description='이름'),
    'email': fields.String(required=True, description='이메일'),
    'phone': fields.String(description='전화번호'),
    'address': fields.String(description='주소'),
    'education': fields.List(fields.Raw, description='학력 정보'),
    'experience': fields.List(fields.Raw, description='경력 정보'),
    'skills': fields.List(fields.String, description='기술 스택'),
    'introduction': fields.String(description='자기소개')
})

response_model = api.model('Response', {
    'success': fields.Boolean(description='성공 여부'),
    'message': fields.String(description='응답 메시지'),
    'text': fields.String(description='추출된 텍스트 (PDF 텍스트 추출 시)')
})

error_model = api.model('Error', {
    'error': fields.String(description='에러 메시지')
})

@health_ns.route('/health')
class HealthCheck(Resource):
    @health_ns.doc('헬스 체크')
    @health_ns.response(200, '서비스 정상')
    def get(self):
        """서비스 헬스 체크"""
        return {
            'status': 'healthy',
            'message': '이력서 변환 서비스가 정상 작동 중입니다.'
        }

@pdf_ns.route('/pdf-to-text')
class PDFToText(Resource):
    @pdf_ns.doc('PDF 텍스트 추출', 
                params={'file': 'PDF 파일 (multipart/form-data)'})
    @pdf_ns.response(200, '텍스트 추출 성공', response_model)
    @pdf_ns.response(400, '잘못된 요청', error_model)
    @pdf_ns.response(500, '서버 오류', error_model)
    def post(self):
        """PDF 파일을 텍스트로 변환"""
        try:
            # multipart/form-data 확인
            if 'multipart/form-data' not in request.headers.get('Content-Type', ''):
                return {'error': 'Content-Type이 multipart/form-data여야 합니다.'}, 400
            
            if 'file' not in request.files:
                return {'error': '파일이 없습니다.'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': '선택된 파일이 없습니다.'}, 400
            
            if not allowed_file(file.filename):
                return {'error': 'PDF 파일만 업로드 가능합니다.'}, 400
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            try:
                # PDF에서 텍스트 추출
                extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
                
                return {
                    'success': True,
                    'text': extracted_text,
                    'message': 'PDF 텍스트 추출이 완료되었습니다.'
                }
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {'error': str(e)}, 500

@pdf_ns.route('/text-to-pdf')
class TextToPDF(Resource):
    @pdf_ns.doc('이력서 PDF 생성')
    @pdf_ns.expect(resume_model)
    @pdf_ns.response(200, 'PDF 생성 성공')
    @pdf_ns.response(400, '잘못된 요청', error_model)
    @pdf_ns.response(500, '서버 오류', error_model)
    def post(self):
        """이력서 데이터를 PDF로 변환"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'JSON 데이터가 없습니다.'}, 400
            
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
            return {'error': str(e)}, 500

@pdf_ns.route('/convert-resume')
class ConvertResume(Resource):
    @pdf_ns.doc('통합 이력서 변환',
                params={'data': 'JSON 데이터 (application/json) 또는 파일 (multipart/form-data)'})
    @pdf_ns.expect(resume_model)
    @pdf_ns.response(200, '변환 성공')
    @pdf_ns.response(400, '잘못된 요청', error_model)
    @pdf_ns.response(500, '서버 오류', error_model)
    def post(self):
        """통합 이력서 변환 (JSON 데이터 또는 파일 업로드)"""
        try:
            # Content-Type 확인
            content_type = request.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                # JSON 데이터로 이력서 변환
                data = request.get_json()
                
                if not data:
                    return {'error': 'JSON 데이터가 없습니다.'}, 400
                
                pdf_content = PDFService.create_pdf_from_data(data)
                
                return send_file(
                    io.BytesIO(pdf_content),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='resume.pdf'
                )
                
            elif 'multipart/form-data' in content_type:
                # 파일 업로드로 PDF 변환
                if 'file' not in request.files:
                    return {'error': '파일이 없습니다.'}, 400
                
                file = request.files['file']
                if file.filename == '':
                    return {'error': '선택된 파일이 없습니다.'}, 400
                
                if not allowed_file(file.filename):
                    return {'error': 'PDF 파일만 업로드 가능합니다.'}, 400
                
                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    file.save(temp_file.name)
                    temp_file_path = temp_file.name
                
                try:
                    # PDF에서 텍스트 추출
                    extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
                    
                    return {
                        'success': True,
                        'text': extracted_text,
                        'message': 'PDF 텍스트 추출이 완료되었습니다.'
                    }
                    
                finally:
                    # 임시 파일 삭제
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            else:
                return {'error': '지원하지 않는 Content-Type입니다.'}, 400
                
        except Exception as e:
            return {'error': str(e)}, 500 