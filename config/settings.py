import os

class Config:
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 최대 파일 크기
    
    # Flask 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # 서버 설정
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5002))
    
    # PDF 설정
    PDF_FONT_NAME = 'Helvetica'  # 기본 폰트
    PDF_PAGE_SIZE = 'A4'
    
    @staticmethod
    def init_app(app):
        """Flask 앱에 설정을 적용합니다."""
        app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        
        # 업로드 폴더가 없으면 생성
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER) 