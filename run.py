#!/usr/bin/env python3
"""
YouTube 바이럴 영상 분석 시스템 테스트 스크립트
"""

import sys
import os

def check_dependencies():
    """필요한 라이브러리들이 설치되어 있는지 확인합니다."""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'googleapiclient', 
        'matplotlib', 'numpy', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 설치됨")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 설치 필요")
    
    if missing_packages:
        print(f"\n⚠️  다음 패키지들을 설치해야 합니다:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_youtube_api():
    """YouTube API 연결을 테스트합니다."""
    try:
        from youtube_api import YouTubeDataCollector
        collector = YouTubeDataCollector()
        print("✅ YouTube API 연결 - 성공")
        return True
    except Exception as e:
        print(f"❌ YouTube API 연결 실패: {e}")
        return False

def test_components():
    """주요 컴포넌트들을 테스트합니다."""
    components = [
        ('config', 'config.py'),
        ('youtube_api', 'youtube_api.py'),
        ('viral_analyzer', 'viral_analyzer.py'),
        ('keyword_analyzer', 'keyword_analyzer.py'),
        ('app', 'app.py')
    ]
    
    all_passed = True
    
    for module_name, file_name in components:
        try:
            __import__(module_name)
            print(f"✅ {file_name} - 정상 작동")
        except Exception as e:
            print(f"❌ {file_name} - 오류: {e}")
            all_passed = False
    
    return all_passed

def main():
    print("🔍 YouTube 바이럴 영상 분석 시스템 - 시작 전 검사")
    print("=" * 50)
    
    # 1. 의존성 확인
    print("\n1. 의존성 라이브러리 확인:")
    deps_ok = check_dependencies()
    
    # 2. 컴포넌트 테스트
    print("\n2. 시스템 컴포넌트 확인:")
    components_ok = test_components()
    
    # 3. YouTube API 테스트
    print("\n3. YouTube API 연결 확인:")
    api_ok = test_youtube_api()
    
    # 결과 출력
    print("\n" + "=" * 50)
    if deps_ok and components_ok and api_ok:
        print("🎉 모든 테스트 통과! 시스템이 정상적으로 작동할 준비가 되었습니다.")
        print("\n🚀 애플리케이션 실행 방법:")
        print("streamlit run app.py")
        print("\n브라우저에서 http://localhost:8501로 접속하세요.")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 위의 오류를 확인하고 수정해주세요.")
        
        if not deps_ok:
            print("\n📦 필요한 패키지를 설치하세요:")
            print("pip install -r requirements.txt")
        
        if not api_ok:
            print("\n🔑 YouTube API 키를 확인하세요:")
            print("config.py 파일의 YOUTUBE_API_KEY 값을 확인해주세요.")

if __name__ == "__main__":
    main() 