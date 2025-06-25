from flask import Flask
from flask_cors import CORS
from config.settings import Config
from routes.pdf_routes import pdf_bp

def create_app():
    """Flask 애플리케이션 팩토리 함수"""
    app = Flask(__name__)
    
    # 설정 적용
    Config.init_app(app)
    
    # CORS 설정
    CORS(app)
    
    # 블루프린트 등록
    app.register_blueprint(pdf_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 