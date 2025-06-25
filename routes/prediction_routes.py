from flask import request
from flask_restx import Namespace, Resource, fields
from services.prediction_service import PredictionService
import logging

logger = logging.getLogger(__name__)

# API 네임스페이스 생성
api = Namespace('predictions', description='기업 확률 예측 API')

# 예측 서비스 인스턴스 생성
prediction_service = PredictionService()

# Swagger 모델 정의
user_data_model = api.model('UserData', {
    'name': fields.String(required=True, description='사용자 이름'),
    'age': fields.Integer(required=True, description='나이'),
    'experience': fields.Float(required=True, description='경력 (년)'),
    'skills': fields.List(fields.String, required=True, description='기술 스택'),
    'education': fields.String(description='학력'),
    'etc': fields.String(description='기타 정보')
})

prediction_response_model = api.model('PredictionResponse', {
    'id': fields.String(description='예측 ID'),
    'probability': fields.Float(description='기업 확률 (0-1)'),
    'confidence': fields.Float(description='신뢰도'),
    'recommendations': fields.List(fields.String, description='추천사항'),
    'user_data': fields.Raw(description='입력된 사용자 데이터'),
    'created_at': fields.String(description='생성 시간'),
    'status': fields.String(description='상태')
})

prediction_list_model = api.model('PredictionList', {
    'predictions': fields.List(fields.Nested(prediction_response_model), description='예측 목록'),
    'total': fields.Integer(description='총 예측 수'),
    'page': fields.Integer(description='현재 페이지'),
    'per_page': fields.Integer(description='페이지당 항목 수')
})

model_info_model = api.model('ModelInfo', {
    'model_loaded': fields.Boolean(description='모델 로드 상태'),
    'model_path': fields.String(description='모델 경로'),
    'model_type': fields.String(description='모델 타입'),
    'version': fields.String(description='모델 버전'),
    'last_updated': fields.String(description='마지막 업데이트 시간')
})

error_model = api.model('Error', {
    'error': fields.String(description='오류 메시지'),
    'code': fields.String(description='오류 코드'),
    'details': fields.String(description='상세 정보')
})

@api.route('/')
class PredictionListResource(Resource):
    """예측 목록 및 새 예측 생성"""
    
    @api.doc('예측 목록 조회')
    @api.response(200, '조회 성공', prediction_list_model)
    def get(self):
        """
        예측 목록을 조회합니다.
        
        쿼리 파라미터:
        - page: 페이지 번호 (기본값: 1)
        - per_page: 페이지당 항목 수 (기본값: 10)
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # TODO: 실제 예측 히스토리 구현
            # 현재는 더미 데이터 반환
            predictions = []
            
            return {
                'predictions': predictions,
                'total': len(predictions),
                'page': page,
                'per_page': per_page
            }, 200
            
        except Exception as e:
            logger.error(f"예측 목록 조회 오류: {str(e)}")
            return {
                'error': '예측 목록 조회 중 오류가 발생했습니다.',
                'code': 'PREDICTION_LIST_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('새 예측 생성')
    @api.expect(user_data_model)
    @api.response(201, '예측 생성 성공', prediction_response_model)
    @api.response(400, '잘못된 요청', error_model)
    @api.response(500, '서버 오류', error_model)
    def post(self):
        """
        새로운 기업 확률 예측을 생성합니다.
        
        입력 데이터:
        - name: 이름 (필수)
        - age: 나이 (필수, 18-100)
        - experience: 경력 (필수, 년 단위)
        - skills: 기술 스택 (필수, 리스트)
        - education: 학력 (선택)
        - etc: 기타 정보 (선택)
        
        반환 데이터:
        - id: 예측 ID
        - probability: 기업 확률 (0-1)
        - confidence: 신뢰도
        - recommendations: 추천사항 리스트
        - user_data: 입력된 사용자 데이터
        - created_at: 생성 시간
        - status: 상태
        """
        try:
            # JSON 데이터 파싱
            user_data = request.get_json()
            
            if not user_data:
                return {
                    'error': '요청 데이터가 없습니다.',
                    'code': 'MISSING_DATA',
                    'details': 'JSON 데이터를 제공해주세요.'
                }, 400
            
            logger.info(f"예측 요청 받음: {user_data.get('name', 'Unknown')}")
            
            # 예측 수행
            result = prediction_service.predict_company_probability(user_data)
            
            if result['success']:
                # 예측 ID 생성 (실제로는 UUID 사용)
                import uuid
                from datetime import datetime
                
                prediction_id = str(uuid.uuid4())
                created_at = datetime.now().isoformat()
                
                response_data = {
                    'id': prediction_id,
                    'probability': result['probability'],
                    'confidence': result['confidence'],
                    'recommendations': result['recommendations'],
                    'user_data': result['user_data'],
                    'created_at': created_at,
                    'status': 'completed'
                }
                
                logger.info(f"예측 완료: {result['probability']:.2f}")
                return response_data, 201
            else:
                logger.warning(f"예측 실패: {result['error']}")
                return {
                    'error': result['error'],
                    'code': 'PREDICTION_FAILED',
                    'details': '예측 처리 중 오류가 발생했습니다.'
                }, 400
                
        except Exception as e:
            logger.error(f"예측 API 오류: {str(e)}")
            return {
                'error': '서버 오류가 발생했습니다.',
                'code': 'SERVER_ERROR',
                'details': str(e)
            }, 500

@api.route('/<string:prediction_id>')
class PredictionResource(Resource):
    """특정 예측 조회, 수정, 삭제"""
    
    @api.doc('특정 예측 조회')
    @api.response(200, '조회 성공', prediction_response_model)
    @api.response(404, '예측을 찾을 수 없음', error_model)
    def get(self, prediction_id):
        """
        특정 예측 결과를 조회합니다.
        
        파라미터:
        - prediction_id: 예측 ID
        """
        try:
            # TODO: 실제 예측 결과 조회 구현
            # 현재는 더미 데이터 반환
            return {
                'error': '예측을 찾을 수 없습니다.',
                'code': 'PREDICTION_NOT_FOUND',
                'details': f'ID {prediction_id}에 해당하는 예측이 없습니다.'
            }, 404
            
        except Exception as e:
            logger.error(f"예측 조회 오류: {str(e)}")
            return {
                'error': '예측 조회 중 오류가 발생했습니다.',
                'code': 'PREDICTION_GET_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('예측 수정')
    @api.expect(user_data_model)
    @api.response(200, '수정 성공', prediction_response_model)
    @api.response(404, '예측을 찾을 수 없음', error_model)
    def put(self, prediction_id):
        """
        특정 예측을 수정합니다.
        
        파라미터:
        - prediction_id: 예측 ID
        """
        try:
            # TODO: 실제 예측 수정 구현
            return {
                'error': '예측을 찾을 수 없습니다.',
                'code': 'PREDICTION_NOT_FOUND',
                'details': f'ID {prediction_id}에 해당하는 예측이 없습니다.'
            }, 404
            
        except Exception as e:
            logger.error(f"예측 수정 오류: {str(e)}")
            return {
                'error': '예측 수정 중 오류가 발생했습니다.',
                'code': 'PREDICTION_UPDATE_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('예측 삭제')
    @api.response(204, '삭제 성공')
    @api.response(404, '예측을 찾을 수 없음', error_model)
    def delete(self, prediction_id):
        """
        특정 예측을 삭제합니다.
        
        파라미터:
        - prediction_id: 예측 ID
        """
        try:
            # TODO: 실제 예측 삭제 구현
            return '', 204
            
        except Exception as e:
            logger.error(f"예측 삭제 오류: {str(e)}")
            return {
                'error': '예측 삭제 중 오류가 발생했습니다.',
                'code': 'PREDICTION_DELETE_ERROR',
                'details': str(e)
            }, 500

@api.route('/model')
class ModelResource(Resource):
    """모델 정보 및 관리"""
    
    @api.doc('모델 정보 조회')
    @api.response(200, '조회 성공', model_info_model)
    def get(self):
        """
        현재 로드된 모델의 정보를 조회합니다.
        
        반환 데이터:
        - model_loaded: 모델 로드 상태
        - model_path: 모델 경로
        - model_type: 모델 타입
        - version: 모델 버전
        - last_updated: 마지막 업데이트 시간
        """
        try:
            model_info = prediction_service.get_model_info()
            from datetime import datetime
            model_info['last_updated'] = datetime.now().isoformat()
            return model_info, 200
            
        except Exception as e:
            logger.error(f"모델 정보 조회 오류: {str(e)}")
            return {
                'error': '모델 정보 조회 중 오류가 발생했습니다.',
                'code': 'MODEL_INFO_ERROR',
                'details': str(e)
            }, 500
    
    @api.doc('모델 로드')
    @api.response(200, '모델 로드 성공')
    @api.response(500, '모델 로드 실패', error_model)
    def post(self):
        """
        예측 모델을 로드합니다.
        
        쿼리 파라미터:
        - model_name: 모델 파일명 (선택사항)
        """
        try:
            model_name = request.args.get('model_name')
            
            logger.info(f"모델 로드 요청: {model_name}")
            
            success = prediction_service.load_model(model_name)
            
            if success:
                return {
                    'message': '모델 로드가 완료되었습니다.',
                    'model_name': model_name
                }, 200
            else:
                return {
                    'error': '모델 로드에 실패했습니다.',
                    'code': 'MODEL_LOAD_FAILED',
                    'details': '모델 파일을 찾을 수 없거나 로드할 수 없습니다.'
                }, 500
                
        except Exception as e:
            logger.error(f"모델 로드 API 오류: {str(e)}")
            return {
                'error': '모델 로드 중 오류가 발생했습니다.',
                'code': 'MODEL_LOAD_ERROR',
                'details': str(e)
            }, 500

@api.route('/health')
class HealthResource(Resource):
    """서비스 상태 확인"""
    
    @api.doc('헬스 체크')
    @api.response(200, '서비스 정상')
    def get(self):
        """
        예측 서비스의 상태를 확인합니다.
        
        반환 데이터:
        - status: 서비스 상태
        - model_loaded: 모델 로드 상태
        - service: 서비스명
        - timestamp: 확인 시간
        """
        try:
            model_info = prediction_service.get_model_info()
            from datetime import datetime
            
            return {
                'status': 'healthy',
                'model_loaded': model_info['model_loaded'],
                'service': 'prediction_service',
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            logger.error(f"헬스 체크 오류: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'service': 'prediction_service',
                'timestamp': datetime.now().isoformat()
            }, 500 