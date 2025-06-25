from flask import Blueprint, request, jsonify, send_file
import tempfile
import os
import io
from services.pdf_service import PDFService
from utils.file_utils import allowed_file, ensure_upload_folder
from config.settings import Config

# PDF 관련 라우트 블루프린트 생성
pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy', 
        'message': '이력서 변환 서비스가 정상 작동 중입니다.'
    })

@pdf_bp.route('/pdf-to-text', methods=['POST'])
def pdf_to_text():
    """PDF 파일을 텍스트로 변환하는 엔드포인트"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '선택된 파일이 없습니다.'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'PDF 파일만 업로드 가능합니다.'}), 400
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # PDF에서 텍스트 추출
            extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
            
            return jsonify({
                'success': True,
                'text': extracted_text,
                'message': 'PDF 텍스트 추출이 완료되었습니다.'
            })
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/text-to-pdf', methods=['POST'])
def text_to_pdf():
    """텍스트 데이터를 PDF로 변환하는 엔드포인트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON 데이터가 없습니다.'}), 400
        
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
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/convert-resume', methods=['POST'])
def convert_resume():
    """통합 이력서 변환 엔드포인트 (JSON 데이터 또는 파일 업로드)"""
    try:
        # Content-Type 확인
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON 데이터로 이력서 변환
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'JSON 데이터가 없습니다.'}), 400
            
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
                return jsonify({'error': '파일이 없습니다.'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '선택된 파일이 없습니다.'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'PDF 파일만 업로드 가능합니다.'}), 400
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            try:
                # PDF에서 텍스트 추출
                extracted_text = PDFService.extract_text_from_pdf(temp_file_path)
                
                return jsonify({
                    'success': True,
                    'text': extracted_text,
                    'message': 'PDF 텍스트 추출이 완료되었습니다.'
                })
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            return jsonify({'error': '지원하지 않는 Content-Type입니다.'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500 