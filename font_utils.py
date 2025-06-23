"""
한글 폰트 처리 유틸리티
"""

import os
import platform
import requests
import subprocess
import sys
from urllib.parse import urlparse

def install_system_fonts():
    """
    배포 환경(Linux)에서 한글 폰트를 시스템에 설치합니다.
    """
    try:
        if platform.system() == 'Linux':
            # apt 패키지 매니저로 한글 폰트 설치 시도
            subprocess.run(['apt-get', 'update'], check=False, capture_output=True)
            subprocess.run(['apt-get', 'install', '-y', 'fonts-nanum'], check=False, capture_output=True)
            
            # fontconfig 캐시 업데이트
            subprocess.run(['fc-cache', '-fv'], check=False, capture_output=True)
            print("✅ 시스템 한글 폰트 설치 시도 완료")
    except Exception as e:
        print(f"⚠️ 시스템 폰트 설치 실패 (권한 문제일 수 있음): {e}")

def get_korean_font_path():
    """
    시스템에서 사용 가능한 한글 폰트 경로를 찾거나 다운로드합니다.
    
    Returns:
        str: 한글 폰트 경로 또는 None
    """
    # 1순위: 로컬 fonts 폴더의 폰트 (배포용)
    local_font_paths = [
        os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf'),
        os.path.join(os.getcwd(), 'fonts', 'NanumGothic.ttf'),
        './fonts/NanumGothic.ttf',
        'fonts/NanumGothic.ttf'
    ]
    
    # 로컬 폰트 우선 확인
    for font_path in local_font_paths:
        if os.path.exists(font_path):
            abs_path = os.path.abspath(font_path)
            print(f"✅ 로컬 폰트 발견: {abs_path}")
            return abs_path
    
    # Windows 시스템의 한글 폰트들
    windows_fonts = [
        'C:/Windows/Fonts/malgun.ttf',      # 맑은 고딕
        'C:/Windows/Fonts/gulim.ttc',       # 굴림
        'C:/Windows/Fonts/batang.ttc',      # 바탕
        'C:/Windows/Fonts/NanumGothic.ttf'  # 나눔고딕 (설치된 경우)
    ]
    
    # macOS 시스템의 한글 폰트들
    mac_fonts = [
        '/System/Library/Fonts/AppleGothic.ttf',
        '/Library/Fonts/NanumGothic.ttf',
        '/System/Library/Fonts/Helvetica.ttc'
    ]
    
    # Linux 시스템의 한글 폰트들 (Streamlit Cloud 포함)
    linux_fonts = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/NanumGothic.ttf',
        '/system/fonts/NanumGothic.ttf'
    ]
    
    system = platform.system()
    
    if system == 'Windows':
        font_candidates = windows_fonts
    elif system == 'Darwin':  # macOS
        font_candidates = mac_fonts
    else:  # Linux 및 기타 (Streamlit Cloud)
        font_candidates = linux_fonts
    
    # 사용 가능한 폰트 찾기
    for font_path in font_candidates:
        if os.path.exists(font_path):
            print(f"✅ 시스템 폰트 발견: {font_path}")
            return font_path
    
    # 시스템 폰트를 찾지 못한 경우
    print("⚠️ 시스템 한글 폰트를 찾을 수 없습니다. 다운로드를 시도합니다...")
    
    # Linux 환경에서 시스템 폰트 설치 시도
    if system == 'Linux':
        install_system_fonts()
        
        # 다시 시스템 폰트 찾기
        for font_path in linux_fonts:
            if os.path.exists(font_path):
                print(f"✅ 설치된 시스템 폰트 발견: {font_path}")
                return font_path
    
    # 마지막으로 다운로드 시도
    return download_nanum_font()

def download_nanum_font():
    """
    나눔고딕 폰트를 다운로드합니다.
    
    Returns:
        str: 다운로드된 폰트 경로 또는 None
    """
    try:
        # 폰트 저장 디렉토리 생성
        font_dir = "fonts"
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)
        
        font_path = os.path.join(font_dir, "NanumGothic.ttf")
        
        # 이미 다운로드된 경우
        if os.path.exists(font_path):
            print(f"✅ 기존 폰트 파일 사용: {font_path}")
            return font_path
        
        # 나눔고딕 폰트 다운로드 URL들 (여러 백업 URL)
        font_urls = [
            "https://github.com/naver/nanumfont/raw/main/fonts/NanumGothic.ttf",
            "https://cdn.jsdelivr.net/gh/naver/nanumfont@main/fonts/NanumGothic.ttf",
            "https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap"
        ]
        
        for font_url in font_urls:
            try:
                print(f"한글 폰트 다운로드 중: {font_url}")
                response = requests.get(font_url, timeout=30)
                response.raise_for_status()
                
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 한글 폰트 다운로드 완료: {font_path}")
                return font_path
                
            except Exception as e:
                print(f"⚠️ {font_url} 다운로드 실패: {e}")
                continue
        
        print("❌ 모든 폰트 다운로드 URL에서 실패했습니다.")
        return None
        
    except Exception as e:
        print(f"⚠️ 한글 폰트 다운로드 실패: {e}")
        return None

def get_fallback_font():
    """
    한글 폰트가 없을 때 사용할 대체 폰트를 찾습니다.
    """
    try:
        import matplotlib.font_manager as fm
        
        # 사용 가능한 폰트 중에서 한글을 지원할 만한 폰트들 찾기
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 우선순위대로 대체 폰트 찾기
        fallback_candidates = [
            'NanumGothic', 'Nanum Gothic', 'Malgun Gothic', 'AppleGothic',
            'DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS'
        ]
        
        for candidate in fallback_candidates:
            if candidate in available_fonts:
                print(f"✅ 대체 폰트 사용: {candidate}")
                return candidate
        
        print("⚠️ 적합한 대체 폰트를 찾을 수 없습니다.")
        return None
        
    except Exception as e:
        print(f"⚠️ 대체 폰트 검색 실패: {e}")
        return None

def setup_matplotlib_korean():
    """
    Matplotlib에서 한글을 표시할 수 있도록 설정합니다.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # 한글 폰트 경로 가져오기
        font_path = get_korean_font_path()
        
        if font_path and os.path.exists(font_path):
            # 폰트 등록
            font_prop = fm.FontProperties(fname=font_path)
            font_name = font_prop.get_name()
            plt.rcParams['font.family'] = font_name
            print(f"✅ Matplotlib 한글 폰트 설정 완료: {font_name}")
        else:
            # 대체 폰트 사용
            fallback_font = get_fallback_font()
            if fallback_font:
                plt.rcParams['font.family'] = fallback_font
                print(f"✅ Matplotlib 대체 폰트 설정: {fallback_font}")
            else:
                print("⚠️ Matplotlib 한글 폰트 설정 실패 - 기본 폰트 사용")
        
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지
        
    except Exception as e:
        print(f"⚠️ Matplotlib 한글 폰트 설정 실패: {e}")

def get_wordcloud_font_path():
    """
    WordCloud에서 사용할 한글 폰트 경로를 반환합니다.
    """
    # 먼저 한글 폰트 경로 시도
    font_path = get_korean_font_path()
    if font_path and os.path.exists(font_path):
        return font_path
    
    # 추가 로컬 폰트 경로들 확인
    additional_local_paths = [
        os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf'),
        './fonts/NanumGothic.ttf',
        'fonts/NanumGothic.ttf'
    ]
    
    for path in additional_local_paths:
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            print(f"✅ WordCloud 로컬 폰트 사용: {abs_path}")
            return abs_path
    
    # 대체 폰트 경로들
    fallback_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/System/Library/Fonts/AppleGothic.ttf',  # macOS
        'C:/Windows/Fonts/malgun.ttf'  # Windows
    ]
    
    for path in fallback_paths:
        if os.path.exists(path):
            print(f"✅ WordCloud 대체 폰트 사용: {path}")
            return path
    
    print("⚠️ WordCloud용 폰트를 찾을 수 없습니다. 폰트 없이 실행됩니다.")
    return None 