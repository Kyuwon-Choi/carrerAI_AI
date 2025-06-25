import os
from werkzeug.utils import secure_filename
from config.settings import Config

def allowed_file(filename):
    """파일 확장자가 허용된 형식인지 확인합니다."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_safe_filename(filename):
    """안전한 파일명을 반환합니다."""
    return secure_filename(filename)

def ensure_upload_folder():
    """업로드 폴더가 존재하는지 확인하고 없으면 생성합니다."""
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

def get_file_extension(filename):
    """파일의 확장자를 반환합니다."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None

def is_pdf_file(filename):
    """파일이 PDF인지 확인합니다."""
    return get_file_extension(filename) == 'pdf' 