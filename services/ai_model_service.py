import joblib
import pandas as pd
import logging
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AIModelService:
    """AI 모델을 사용한 기업 확률 예측 서비스"""
    
    def __init__(self):
        self.model = None
        self.label_map = None
        self.label_reverse_map = None
        self.model_loaded = False
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        # 사후 가중치 설정
        self.post_weights = {
            '삼성전자': 1.3,
            'LG전자': 1.2,
            '현대자동차': 1.2
        }
    
    def load_model(self) -> bool:
        """
        AI 모델과 라벨맵을 로드합니다.
        
        Returns:
            bool: 모델 로드 성공 여부
        """
        try:
            model_path = os.path.join(self.models_dir, 'xgb_model.pkl')
            label_map_path = os.path.join(self.models_dir, 'label_map.pkl')
            
            if not os.path.exists(model_path):
                logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
                return False
                
            if not os.path.exists(label_map_path):
                logger.error(f"라벨맵 파일을 찾을 수 없습니다: {label_map_path}")
                return False
            
            # 모델과 라벨맵 로드
            self.model = joblib.load(model_path)
            self.label_map = joblib.load(label_map_path)
            self.label_reverse_map = {v: k for k, v in self.label_map.items()}
            
            self.model_loaded = True
            logger.info("AI 모델 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {str(e)}")
            self.model_loaded = False
            return False
    
    def predict_company_probabilities(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """
        사용자 데이터를 기반으로 기업별 확률을 예측합니다.
        
        Args:
            user_data: 사용자 정보 딕셔너리
                - age: 나이
                - school: 학교 (라벨값)
                - major: 전공 (라벨값)
                - gpa: 학점
                - language_score: 어학점수 (라벨값)
                - activity_score: 대외활동점수
                - internship_score: 인턴경험점수
                - award_score: 수상경험점수
                
        Returns:
            Dict[str, float]: 기업별 확률 (퍼센트)
        """
        try:
            if not self.model_loaded:
                raise Exception("모델이 로드되지 않았습니다.")
            
            # 입력 데이터 검증
            if not self._validate_input_data(user_data):
                raise Exception("입력 데이터가 유효하지 않습니다.")
            
            # DataFrame 생성 (컬럼 순서 맞춰야 함)
            new_input = pd.DataFrame([{
                '나이': user_data['age'],
                '학교': user_data['school'],
                '전공': user_data['major'],
                '학점': user_data['gpa'],
                '어학점수': user_data['language_score'],
                '대외활동점수': user_data['activity_score'],
                '인턴경험점수': user_data['internship_score'],
                '수상경험점수': user_data['award_score']
            }])
            
            # 원래 예측 확률
            probas = self.model.predict_proba(new_input)[0]
            
            # 가중치 적용 및 정규화
            adjusted = []
            for i, prob in enumerate(probas):
                company = self.label_reverse_map[i]
                weight = self.post_weights.get(company, 1.0)  # 기본값 1.0
                adjusted.append((company, prob * weight))
            
            # 정규화
            total = sum(prob for _, prob in adjusted)
            normalized = [(company, prob / total * 100) for company, prob in adjusted]
            
            # 내림차순 정렬
            sorted_results = sorted(normalized, key=lambda x: x[1], reverse=True)
            
            # 딕셔너리로 변환
            result = {company: round(prob, 2) for company, prob in sorted_results}
            
            logger.info(f"예측 완료: {len(result)}개 기업")
            return result
            
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {str(e)}")
            raise e
    
    def _validate_input_data(self, user_data: Dict[str, Any]) -> bool:
        """
        입력 데이터의 유효성을 검증합니다.
        
        Args:
            user_data: 검증할 사용자 데이터
            
        Returns:
            bool: 유효성 검증 결과
        """
        required_fields = [
            'age', 'school', 'major', 'gpa', 
            'language_score', 'activity_score', 
            'internship_score', 'award_score'
        ]
        
        for field in required_fields:
            if field not in user_data or user_data[field] is None:
                logger.warning(f"필수 필드 누락: {field}")
                return False
        
        # 나이 검증
        if not isinstance(user_data['age'], (int, float)) or user_data['age'] < 18 or user_data['age'] > 100:
            logger.warning("나이가 유효하지 않습니다")
            return False
        
        # 학점 검증
        if not isinstance(user_data['gpa'], (int, float)) or user_data['gpa'] < 0 or user_data['gpa'] > 4.5:
            logger.warning("학점이 유효하지 않습니다")
            return False
        
        # 점수 검증
        score_fields = ['activity_score', 'internship_score', 'award_score']
        for field in score_fields:
            if not isinstance(user_data[field], (int, float)) or user_data[field] < 0:
                logger.warning(f"{field}가 유효하지 않습니다")
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 로드된 모델의 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            'model_loaded': self.model_loaded,
            'model_path': os.path.join(self.models_dir, 'xgb_model.pkl'),
            'label_map_path': os.path.join(self.models_dir, 'label_map.pkl'),
            'model_type': 'XGBoost',
            'version': '1.0',
            'post_weights': self.post_weights,
            'companies_count': len(self.label_reverse_map) if self.label_reverse_map else 0
        } 