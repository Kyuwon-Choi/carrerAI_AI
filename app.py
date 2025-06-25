from flask import Flask, request, send_file
from flask_cors import CORS
from flask_restx import Api
from config.settings import Config
from routes.pdf_routes import api as pdf_api
from routes.prediction_routes import api as prediction_api
from routes.ai_routes import api as ai_api
from services.pdf_service import PDFService
from services.resume_parser_service import ResumeParserService
from utils.file_utils import allowed_file
import tempfile
import os
import io

def create_app():
    """Flask 애플리케이션 팩토리 함수"""
    app = Flask(__name__)
    
    # 설정 적용
    Config.init_app(app)
    
    # CORS 설정
    CORS(app)
    
    # Flask-RESTX API 객체 생성 (Swagger 2.0 사용)
    api = Api(app, 
              version='1.0', 
              title='CareerAI API',
              description='이력서 PDF 변환 및 기업 확률 예측 API',
              doc='/docs',
              authorizations={
                  'apikey': {
                      'type': 'apiKey',
                      'in': 'header',
                      'name': 'X-API-KEY'
                  }
              },
              security='apikey',
              default='default',
              default_label='CareerAI API',
              validate=True,
              prefix='/api',
              # Swagger 2.0 설정
              swagger_ui_bundle_js='//cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js',
              swagger_ui_standalone_preset_js='//cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js',
              swagger_ui_css='//cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css',
              swagger_ui_js='//cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.js',
              # Swagger 2.0 명시적 설정
              swagger_ui_parameters={
                  'swagger': '2.0',
                  'info': {
                      'title': 'CareerAI API',
                      'version': '1.0',
                      'description': '이력서 PDF 변환 및 기업 확률 예측 API'
                  }
              })
    
    # API 네임스페이스 등록
    api.add_namespace(pdf_api, path='/documents')
    api.add_namespace(prediction_api, path='/predictions')
    api.add_namespace(ai_api, path='/ai')
    
    # 기존 URL과의 호환성을 위한 추가 라우트
    @app.route('/analyze-probability', methods=['POST'])
    def legacy_analyze_probability():
        """
        스프링과의 호환성을 위한 기업 확률 분석 엔드포인트
        """
        try:
            # JSON 데이터 파싱
            request_data = request.get_json()
            
            if not request_data:
                return {
                    'error': '요청 데이터가 없습니다.',
                    'code': 'MISSING_DATA',
                    'details': 'JSON 데이터를 제공해주세요.'
                }, 400
            
            # AI 모델 서비스 임포트
            from services.ai_model_service import AIModelService
            ai_service = AIModelService()
            
            # AI 모델이 로드되지 않았다면 로드 시도
            if not ai_service.model_loaded:
                if not ai_service.load_model():
                    return {
                        'error': 'AI 모델을 로드할 수 없습니다.',
                        'code': 'MODEL_LOAD_FAILED',
                        'details': '모델 파일을 확인해주세요.'
                    }, 500
            
            # 예측 수행
            probabilities = ai_service.predict_company_probabilities(request_data)
            
            # 가장 높은 확률의 기업 찾기
            top_company = max(probabilities.items(), key=lambda x: x[1])
            
            response_data = {
                'success': True,
                'probabilities': probabilities,
                'top_company': top_company[0],
                'top_probability': top_company[1],
                'message': '분석이 완료되었습니다.'
            }
            
            return response_data, 200
                
        except Exception as e:
            return {
                'error': '분석 중 오류가 발생했습니다.',
                'code': 'ANALYSIS_ERROR',
                'details': str(e)
            }, 500

    @app.route('/documents/convert', methods=['POST'])
    def legacy_document_convert():
        """
        기존 URL과의 호환성을 위한 PDF 텍스트 변환 엔드포인트
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
                # PDF에서 텍스트 추출
                extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
                
                from datetime import datetime
                import uuid
                
                return {
                    'id': str(uuid.uuid4()),
                    'type': 'text',
                    'content': extracted_text,
                    'file_size': len(extracted_text.encode('utf-8')),
                    'created_at': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            return {
                'error': '텍스트 추출 중 오류가 발생했습니다.',
                'code': 'TEXT_EXTRACTION_ERROR',
                'details': str(e)
            }, 500

    @app.route('/documents/parse-resume', methods=['POST'])
    def legacy_resume_parse():
        """
        기존 URL과의 호환성을 위한 이력서 PDF 파싱 엔드포인트
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
                # PDF에서 텍스트 추출
                extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
                
                if not extracted_text:
                    return {
                        'error': 'PDF에서 텍스트를 추출할 수 없습니다.',
                        'code': 'NO_TEXT_EXTRACTED',
                        'details': 'PDF 파일이 텍스트를 포함하지 않거나 이미지로만 구성되어 있습니다.'
                    }, 400
                
                # 이력서 정보 파싱
                parsed_resume = ResumeParserService.parse_resume(extracted_text)
                
                from datetime import datetime
                import uuid
                
                return {
                    'id': str(uuid.uuid4()),
                    'type': 'parsed_resume',
                    'parsed_data': parsed_resume,
                    'raw_text': extracted_text,
                    'file_size': len(extracted_text.encode('utf-8')),
                    'created_at': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            return {
                'error': '이력서 파싱 중 오류가 발생했습니다.',
                'code': 'RESUME_PARSING_ERROR',
                'details': str(e)
            }, 500

    @app.route('/')
    def index():
        return {
            'message': 'CareerAI API 서버가 실행 중입니다.',
            'version': '1.0',
            'endpoints': {
                'swagger_docs': '/docs',
                'api_base': '/api',
                'pdf_conversion': '/api/documents/convert',
                'resume_parsing': '/api/documents/parse-resume',
                'prediction': '/api/predictions/',
                'legacy_pdf_conversion': '/documents/convert',
                'legacy_resume_parsing': '/documents/parse-resume'
            }
        }

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 