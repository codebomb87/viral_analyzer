"""
YouTube 바이럴 영상 분석 시스템 설정
"""

# YouTube API 설정
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Streamlit secrets 또는 환경변수에서 API 키 가져오기
try:
    import streamlit as st
    YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY"))
except:
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY를 환경변수 또는 Streamlit secrets에 설정해주세요.")

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# 바이럴 판별 기준 설정
VIRAL_THRESHOLDS = {
    "views_per_day": 10000,  # 일일 최소 조회수
    "like_ratio": 0.02,      # 최소 좋아요 비율
    "comment_ratio": 0.001,  # 최소 댓글 비율
    "engagement_score": 50   # 최소 참여도 점수
}

# 검색 기본 설정
DEFAULT_MAX_RESULTS = 50
DEFAULT_ORDER = "relevance"  # relevance, date, rating, viewCount, title

# 지원하는 언어
SUPPORTED_LANGUAGES = ["ko", "en"]

# 키워드 분석 설정
STOPWORDS_KO = [
    # 한국어 조사 및 접속사
    "그", "를", "을", "에", "의", "가", "이", "은", "는", "와", "과", "로", "으로",
    "에서", "까지", "부터", "보다", "처럼", "같이", "하고", "하지만", "그리고",
    "그런데", "하지만", "그러나", "따라서", "왜냐하면", "때문에", "입니다", "습니다",
    "해요", "이에요", "예요", "네요", "요", "다", "야", "아", "어", "여",
    
    # URL 및 웹 관련
    "www", "http", "https", "com", "net", "org", "kr", "co", "go", "html",
    "php", "asp", "jsp", "url", "link", "site", "page", "web", "blog",
    
    # YouTube 및 SNS 관련
    "youtube", "youtu", "be", "watch", "video", "channel", "subscribe",
    "like", "comment", "share", "follow", "instagram", "facebook", "twitter",
    "tiktok", "shorts", "live", "stream", "streaming",
    
    # 일반적인 불용어
    "더", "많은", "정말", "진짜", "완전", "너무", "아주", "매우", "정말로",
    "이런", "저런", "그런", "어떤", "무슨", "어느", "모든", "전체", "일부",
    "각각", "각자", "서로", "함께", "같이", "모두", "전부", "하나", "둘", "셋",
    
    # 시간 관련
    "오늘", "어제", "내일", "지금", "현재", "과거", "미래", "언제", "항상",
    "가끔", "종종", "자주", "때때로", "이제", "벌써", "아직", "still", "already",
    
    # 감탄사 및 추임새
    "아", "어", "오", "우", "와", "워", "음", "으", "흠", "헉", "어머", "세상",
    "대박", "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅜㅜ", "ㅇㅇ", "ㄷㄷ", "ㅉㅉ",
    
    # 숫자 및 단위
    "개", "명", "번", "회", "차", "등", "위", "순", "째", "년", "월", "일",
    "시", "분", "초", "원", "만", "억", "천", "백", "십"
]

# 영어 불용어 확장
STOPWORDS_EN = [
    # 기본 불용어
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "by", "as", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "this", "that", "these", "those",
    
    # URL 및 웹 관련
    "www", "http", "https", "com", "net", "org", "html", "php", "asp",
    "url", "link", "site", "page", "web", "blog", "domain", "server",
    
    # YouTube 및 미디어 관련
    "youtube", "video", "watch", "channel", "subscribe", "like", "comment",
    "share", "view", "views", "subscriber", "followers", "content",
    "media", "social", "platform", "streaming", "live", "upload",
    
    # 일반적인 단어
    "more", "most", "very", "really", "just", "only", "also", "even",
    "still", "already", "yet", "now", "then", "here", "there", "where",
    "what", "when", "why", "how", "who", "which", "all", "some", "any",
    "each", "every", "both", "either", "neither", "other", "another"
]

# Streamlit 페이지 설정
PAGE_CONFIG = {
    "page_title": "YouTube 바이럴 영상 분석기",
    "page_icon": "📺",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
} 