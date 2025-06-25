from flask import request
from flask_restx import Namespace, Resource, fields
from services.ai_model_service import AIModelService
import logging

logger = logging.getLogger(__name__)

# API 네임스페이스 생성
api = Namespace('ai', description='AI 모델 분석 API')

# AI 모델 서비스 인스턴스 생성
ai_service = AIModelService()

# Swagger 모델 정의
analysis_request_model = api.model('AnalysisRequest', {
    'user_id': fields.Integer(required=True, description='사용자 ID'),
    'recruitment_id': fields.Integer(required=True, description='채용공고 ID'),
    'job_category': fields.String(required=True, description='직무 카테고리'),
    'age': fields.Float(required=True, description='나이'),
    'school': fields.Float(required=True, description='학교 라벨값'),
    'major': fields.Float(required=True, description='전공 라벨값'),
    'gpa': fields.Float(required=True, description='학점'),
    'language_score': fields.Float(required=True, description='어학점수 라벨값'),
    'activity_score': fields.Float(required=True, description='대외활동점수'),
    'internship_score': fields.Float(required=True, description='인턴경험점수'),
    'award_score': fields.Float(required=True, description='수상경험점수')
})

analysis_response_model = api.model('AnalysisResponse', {
    'success': fields.Boolean(description='성공 여부'),
    'probabilities': fields.Raw(description='기업별 확률 (퍼센트)'),
    'top_company': fields.String(description='가장 높은 확률의 기업'),
    'top_probability': fields.Float(description='가장 높은 확률'),
    'message': fields.String(description='응답 메시지')
})

error_model = api.model('Error', {
    'error': fields.String(description='오류 메시지'),
    'code': fields.String(description='오류 코드'),
    'details': fields.String(description='상세 정보')
})

@api.route('/analyze-probability')
class AnalyzeProbabilityResource(Resource):
    """기업 확률 분석 엔드포인트"""
    
    @api.doc('기업 확률 분석')
    @api.expect(analysis_request_model)
    @api.response(200, '분석 성공', analysis_response_model)
    @api.response(400, '잘못된 요청', error_model)
    @api.response(500, '서버 오류', error_model)
    def post(self):
        """
        사용자 데이터를 기반으로 기업별 확률을 분석합니다.
        
        스프링에서 전송하는 데이터:
        - user_id: 사용자 ID
        - recruitment_id: 채용공고 ID
        - job_category: 직무 카테고리
        - age: 나이
        - school: 학교 라벨값
        - major: 전공 라벨값
        - gpa: 학점
        - language_score: 어학점수 라벨값
        - activity_score: 대외활동점수
        - internship_score: 인턴경험점수
        - award_score: 수상경험점수
        
        반환 데이터:
        - success: 성공 여부
        - probabilities: 기업별 확률 (퍼센트)
        - top_company: 가장 높은 확률의 기업
        - top_probability: 가장 높은 확률
        - message: 응답 메시지
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
            
            logger.info(f"분석 요청 받음: user_id={request_data.get('user_id')}, recruitment_id={request_data.get('recruitment_id')}")
            
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
            
            logger.info(f"분석 완료: top_company={top_company[0]}, probability={top_company[1]:.2f}%")
            return response_data, 200
                
        except Exception as e:
            logger.error(f"분석 API 오류: {str(e)}")
            return {
                'error': '분석 중 오류가 발생했습니다.',
                'code': 'ANALYSIS_ERROR',
                'details': str(e)
            }, 500

@api.route('/model/load')
class ModelLoadResource(Resource):
    """AI 모델 로드 엔드포인트"""
    
    @api.doc('AI 모델 로드')
    @api.response(200, '모델 로드 성공')
    @api.response(500, '모델 로드 실패', error_model)
    def post(self):
        """
        AI 모델을 로드합니다.
        """
        try:
            success = ai_service.load_model()
            
            if success:
                return {
                    'success': True,
                    'message': 'AI 모델이 성공적으로 로드되었습니다.'
                }, 200
            else:
                return {
                    'error': 'AI 모델 로드에 실패했습니다.',
                    'code': 'MODEL_LOAD_FAILED',
                    'details': '모델 파일을 확인해주세요.'
                }, 500
                
        except Exception as e:
            logger.error(f"모델 로드 오류: {str(e)}")
            return {
                'error': '모델 로드 중 오류가 발생했습니다.',
                'code': 'MODEL_LOAD_ERROR',
                'details': str(e)
            }, 500

@api.route('/model/info')
class ModelInfoResource(Resource):
    """AI 모델 정보 조회 엔드포인트"""
    
    @api.doc('AI 모델 정보 조회')
    @api.response(200, '조회 성공')
    def get(self):
        """
        현재 로드된 AI 모델의 정보를 조회합니다.
        """
        try:
            model_info = ai_service.get_model_info()
            return model_info, 200
            
        except Exception as e:
            logger.error(f"모델 정보 조회 오류: {str(e)}")
            return {
                'error': '모델 정보 조회 중 오류가 발생했습니다.',
                'code': 'MODEL_INFO_ERROR',
                'details': str(e)
            }, 500 