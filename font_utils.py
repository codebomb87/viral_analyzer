"""
한글 폰트 처리 유틸리티
"""

import os
import platform
import requests
from urllib.parse import urlparse

def get_korean_font_path():
    """
    시스템에서 사용 가능한 한글 폰트 경로를 찾거나 다운로드합니다.
    
    Returns:
        str: 한글 폰트 경로 또는 None
    """
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
    
    # Linux 시스템의 한글 폰트들
    linux_fonts = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
    ]
    
    system = platform.system()
    
    if system == 'Windows':
        font_candidates = windows_fonts
    elif system == 'Darwin':  # macOS
        font_candidates = mac_fonts
    else:  # Linux 및 기타
        font_candidates = linux_fonts
    
    # 사용 가능한 폰트 찾기
    for font_path in font_candidates:
        if os.path.exists(font_path):
            return font_path
    
    # 폰트를 찾지 못한 경우 나눔고딕 다운로드 시도
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
            return font_path
        
        # 나눔고딕 폰트 다운로드 URL (GitHub에서 제공)
        font_url = "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothic.ttf"
        
        print("한글 폰트를 다운로드 중입니다...")
        response = requests.get(font_url, timeout=30)
        response.raise_for_status()
        
        with open(font_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 한글 폰트 다운로드 완료: {font_path}")
        return font_path
        
    except Exception as e:
        print(f"⚠️ 한글 폰트 다운로드 실패: {e}")
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
            plt.rcParams['font.family'] = font_prop.get_name()
        else:
            # 시스템 폰트 사용
            if 'malgun' in [f.name.lower() for f in fm.fontManager.ttflist]:
                plt.rcParams['font.family'] = 'Malgun Gothic'
            elif 'nanumgothic' in [f.name.lower() for f in fm.fontManager.ttflist]:
                plt.rcParams['font.family'] = 'NanumGothic'
        
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지
        
    except Exception as e:
        print(f"⚠️ Matplotlib 한글 폰트 설정 실패: {e}") 