import pdfplumber
import tempfile
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from config.settings import Config

class PDFService:
    """PDF 관련 서비스 클래스"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """PDF 파일에서 텍스트를 추출합니다."""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF 텍스트 추출 중 오류 발생: {str(e)}")
    
    @staticmethod
    def create_pdf_from_data(resume_data):
        """이력서 데이터를 PDF로 변환합니다."""
        try:
            # PDF 버퍼 생성
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # 스타일 가져오기
            styles = getSampleStyleSheet()
            
            # 기본 폰트 사용
            font_name = Config.PDF_FONT_NAME
            
            # 제목 스타일
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # 중앙 정렬
                fontName=font_name
            )
            
            # 섹션 제목 스타일
            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkblue,
                fontName=font_name
            )
            
            # 내용 스타일
            content_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                fontName=font_name
            )
            
            # 제목 추가
            story.append(Paragraph(resume_data.get('name', 'Resume'), title_style))
            story.append(Spacer(1, 20))
            
            # 기본 정보
            story.append(Paragraph('Basic Information', section_style))
            basic_info = [
                ['Name:', resume_data.get('name', '')],
                ['Email:', resume_data.get('email', '')],
                ['Phone:', resume_data.get('phone', '')],
                ['Address:', resume_data.get('address', '')]
            ]
            basic_table = Table(basic_info, colWidths=[1.5*inch, 4*inch])
            basic_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), font_name),
                ('FONTNAME', (1, 0), (1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(basic_table)
            story.append(Spacer(1, 12))
            
            # 학력
            if resume_data.get('education'):
                story.append(Paragraph('Education', section_style))
                for edu in resume_data.get('education', []):
                    edu_text = f"{edu.get('school', '')} ({edu.get('period', '')})<br/>"
                    edu_text += f"{edu.get('major', '')} - {edu.get('degree', '')}"
                    story.append(Paragraph(edu_text, content_style))
                    story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))
            
            # 경력
            if resume_data.get('experience'):
                story.append(Paragraph('Experience', section_style))
                for exp in resume_data.get('experience', []):
                    exp_text = f"<b>{exp.get('company', '')}</b> ({exp.get('period', '')})<br/>"
                    exp_text += f"<b>{exp.get('position', '')}</b><br/>"
                    exp_text += f"{exp.get('description', '')}"
                    story.append(Paragraph(exp_text, content_style))
                    story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))
            
            # 기술 스택
            if resume_data.get('skills'):
                story.append(Paragraph('Skills', section_style))
                skills_text = ', '.join(resume_data.get('skills', []))
                story.append(Paragraph(skills_text, content_style))
                story.append(Spacer(1, 12))
            
            # 자기소개
            if resume_data.get('introduction'):
                story.append(Paragraph('Introduction', section_style))
                story.append(Paragraph(resume_data.get('introduction', ''), content_style))
            
            # PDF 생성
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"PDF 생성 중 오류 발생: {str(e)}")
    
    @staticmethod
    def html_to_pdf(html_content):
        """HTML을 PDF로 변환합니다. (호환성을 위해 유지)"""
        # 이 함수는 더 이상 사용하지 않지만 호환성을 위해 유지
        pass 