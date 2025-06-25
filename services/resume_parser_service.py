import re
from datetime import datetime
from typing import Dict, List, Any

class ResumeParserService:
    """이력서 파싱 서비스 클래스"""
    
    @staticmethod
    def parse_resume(text: str) -> Dict[str, Any]:
        """
        이력서 텍스트를 구조화된 데이터로 파싱합니다.
        
        Args:
            text: PDF에서 추출한 이력서 텍스트
            
        Returns:
            파싱된 이력서 데이터 딕셔너리
        """
        try:
            # 텍스트 전처리
            cleaned_text = ResumeParserService._preprocess_text(text)
            
            # 각 섹션 파싱
            parsed_data = {
                'phone': ResumeParserService._extract_phone(cleaned_text),
                'email': ResumeParserService._extract_email(cleaned_text),
                'introduction': ResumeParserService._extract_introduction(cleaned_text),
                'experiences': ResumeParserService._extract_experiences(cleaned_text),
                'skills': ResumeParserService._extract_skills(cleaned_text),
                'links': ResumeParserService._extract_links(cleaned_text),
                'awards': ResumeParserService._extract_awards(cleaned_text),
                'certificates': ResumeParserService._extract_certificates(cleaned_text),
                'languages': ResumeParserService._extract_languages(cleaned_text),
                'projects': ResumeParserService._extract_projects(cleaned_text)
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"이력서 파싱 중 오류 발생: {str(e)}")
    
    @staticmethod
    def _preprocess_text(text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 줄바꿈 정리
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    @staticmethod
    def _extract_phone(text: str) -> str:
        """핸드폰 번호 추출"""
        # 한국 휴대폰 번호 패턴
        phone_patterns = [
            r'01[016789]-?\d{3,4}-?\d{4}',  # 010-1234-5678
            r'01[016789]\s?\d{3,4}\s?\d{4}',  # 010 1234 5678
            r'\+82-10-\d{4}-\d{4}',  # +82-10-1234-5678
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        
        return ""
    
    @staticmethod
    def _extract_email(text: str) -> str:
        """이메일 주소 추출"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else ""
    
    @staticmethod
    def _extract_introduction(text: str) -> str:
        """자기소개 추출"""
        # 자기소개 관련 키워드 찾기
        intro_keywords = ['자기소개', '소개', 'About', 'Profile', 'Introduction']
        
        for keyword in intro_keywords:
            # 키워드 다음 200자 정도 추출
            pattern = rf'{keyword}[:\s]*([^\n]{{0,200}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    @staticmethod
    def _extract_experiences(text: str) -> List[Dict[str, str]]:
        """경력 정보 추출"""
        experiences = []
        
        # 경력 관련 섹션 찾기
        experience_sections = [
            '경력', 'Experience', 'Work Experience', 'Career',
            '업무 경험', '직장 경험', '회사 경험'
        ]
        
        for section in experience_sections:
            # 섹션 시작 위치 찾기
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                # 다음 섹션까지 텍스트 추출
                section_text = text[start_pos:start_pos + 2000]  # 2000자 제한
                
                # 회사명과 기간 패턴 찾기
                company_patterns = [
                    r'([가-힣a-zA-Z\s&]+)\s*\(?(\d{4}\.?\d{2})\s*[-~]\s*(\d{4}\.?\d{2}|현재|Present)\)?',
                    r'([가-힣a-zA-Z\s&]+)\s*(\d{4}\.?\d{2})\s*[-~]\s*(\d{4}\.?\d{2}|현재|Present)',
                ]
                
                for pattern in company_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        company = match.group(1).strip()
                        start_date = match.group(2)
                        end_date = match.group(3)
                        
                        # 직책 정보 찾기 (회사명 다음 줄에서)
                        position = ""
                        lines = section_text.split('\n')
                        for i, line in enumerate(lines):
                            if company in line:
                                if i + 1 < len(lines):
                                    position = lines[i + 1].strip()
                                break
                        
                        experiences.append({
                            'company': company,
                            'start_date': start_date,
                            'end_date': end_date,
                            'position': position,
                            'description': ""
                        })
                
                break  # 첫 번째 매칭되는 섹션만 처리
        
        return experiences
    
    @staticmethod
    def _extract_skills(text: str) -> List[Dict[str, str]]:
        """스킬 정보 추출"""
        skills = []
        
        # 스킬 관련 섹션 찾기
        skill_sections = [
            '기술', 'Skills', 'Technical Skills', 'Programming Languages',
            '프로그래밍 언어', '개발 도구', 'Tools'
        ]
        
        for section in skill_sections:
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                section_text = text[start_pos:start_pos + 1000]
                
                # 기술명 추출 (쉼표, 줄바꿈으로 구분)
                skill_names = re.split(r'[,，\n]', section_text)
                
                for skill_name in skill_names:
                    skill_name = skill_name.strip()
                    if skill_name and len(skill_name) > 1:
                        skills.append({
                            'name': skill_name,
                            'level': ""
                        })
                
                break
        
        return skills
    
    @staticmethod
    def _extract_links(text: str) -> List[Dict[str, str]]:
        """링크 정보 추출"""
        links = []
        
        # URL 패턴 찾기
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            link_type = "other"
            
            # 링크 타입 분류
            if 'github.com' in url:
                link_type = "github"
            elif 'blog' in url or 'tistory.com' in url or 'velog.io' in url:
                link_type = "blog"
            elif 'linkedin.com' in url:
                link_type = "linkedin"
            elif 'portfolio' in url:
                link_type = "portfolio"
            
            links.append({
                'type': link_type,
                'url': url
            })
        
        return links
    
    @staticmethod
    def _extract_awards(text: str) -> List[Dict[str, str]]:
        """수상 정보 추출"""
        awards = []
        
        # 수상 관련 섹션 찾기
        award_sections = [
            '수상', 'Awards', 'Achievements', '수상 경력',
            '상', 'Award', 'Achievement'
        ]
        
        for section in award_sections:
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                section_text = text[start_pos:start_pos + 1000]
                
                # 수상명과 날짜 패턴 찾기
                award_patterns = [
                    r'([^,\n]+)\s*\(?(\d{4}\.?\d{2})\)?',
                    r'([^,\n]+)\s*(\d{4}\.?\d{2})',
                ]
                
                for pattern in award_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        title = match.group(1).strip()
                        date = match.group(2)
                        
                        awards.append({
                            'title': title,
                            'date': date,
                            'organization': ""
                        })
                
                break
        
        return awards
    
    @staticmethod
    def _extract_certificates(text: str) -> List[Dict[str, str]]:
        """자격증 정보 추출"""
        certificates = []
        
        # 자격증 관련 섹션 찾기
        cert_sections = [
            '자격증', 'Certificates', 'Certifications', 'License',
            '자격', 'Certificate', 'Certification'
        ]
        
        for section in cert_sections:
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                section_text = text[start_pos:start_pos + 1000]
                
                # 자격증명과 날짜 패턴 찾기
                cert_patterns = [
                    r'([^,\n]+)\s*\(?(\d{4}\.?\d{2})\)?',
                    r'([^,\n]+)\s*(\d{4}\.?\d{2})',
                ]
                
                for pattern in cert_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        name = match.group(1).strip()
                        date = match.group(2)
                        
                        certificates.append({
                            'name': name,
                            'date': date,
                            'organization': ""
                        })
                
                break
        
        return certificates
    
    @staticmethod
    def _extract_languages(text: str) -> List[Dict[str, str]]:
        """어학 정보 추출"""
        languages = []
        
        # 어학 관련 섹션 찾기
        lang_sections = [
            '어학', 'Languages', 'Language Skills', '외국어',
            'Language', '외국어 능력'
        ]
        
        for section in lang_sections:
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                section_text = text[start_pos:start_pos + 500]
                
                # 언어명과 수준 패턴 찾기
                lang_patterns = [
                    r'([가-힣a-zA-Z]+)\s*[:\s]*([가-힣a-zA-Z]+)',
                    r'([가-힣a-zA-Z]+)\s*\(([가-힣a-zA-Z]+)\)',
                ]
                
                for pattern in lang_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        name = match.group(1).strip()
                        level = match.group(2).strip()
                        
                        languages.append({
                            'name': name,
                            'level': level
                        })
                
                break
        
        return languages
    
    @staticmethod
    def _extract_projects(text: str) -> List[Dict[str, Any]]:
        """프로젝트 경험 추출"""
        projects = []
        
        # 프로젝트 관련 섹션 찾기
        project_sections = [
            '프로젝트', 'Projects', 'Project Experience', '개발 프로젝트',
            'Project', 'Portfolio'
        ]
        
        for section in project_sections:
            section_match = re.search(rf'{section}[:\s]*', text, re.IGNORECASE)
            if section_match:
                start_pos = section_match.end()
                section_text = text[start_pos:start_pos + 2000]
                
                # 프로젝트명과 기간 패턴 찾기
                project_patterns = [
                    r'([^,\n]+)\s*\(?(\d{4}\.?\d{2}\s*[-~]\s*\d{4}\.?\d{2})\)?',
                    r'([^,\n]+)\s*(\d{4}\.?\d{2}\s*[-~]\s*\d{4}\.?\d{2})',
                ]
                
                for pattern in project_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        name = match.group(1).strip()
                        period = match.group(2)
                        
                        projects.append({
                            'name': name,
                            'period': period,
                            'description': "",
                            'technologies': []
                        })
                
                break
        
        return projects 