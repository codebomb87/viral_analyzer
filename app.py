"""
YouTube 바이럴 영상 분석 시스템 - Streamlit 메인 애플리케이션
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import config
from youtube_api import YouTubeDataCollector
from viral_analyzer import ViralAnalyzer
from keyword_analyzer import KeywordAnalyzer

# 한글 폰트 설정 초기화
try:
    from font_utils import setup_matplotlib_korean, get_korean_font_path
    
    # 폰트 경로 미리 확인
    font_path = get_korean_font_path()
    if font_path:
        print(f"✅ 한글 폰트 발견: {font_path}")
    else:
        print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    
    # Matplotlib 한글 폰트 설정
    setup_matplotlib_korean()
    
except Exception as e:
    print(f"폰트 설정 오류: {e}")
    # 기본 설정으로 진행
    import matplotlib.pyplot as plt
    plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(**config.PAGE_CONFIG)

# 세션 상태 초기화
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'last_search_params' not in st.session_state:
    st.session_state.last_search_params = {}

def main():
    st.title("📺 YouTube 바이럴 영상 분석기")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🔍 검색 설정")
        
        # 모든 검색 설정을 하나의 폼으로 통합
        with st.form("search_form", clear_on_submit=False):
            # 검색 키워드
            search_query = st.text_input("검색 키워드", value="", placeholder="키워드 입력 후 검색 버튼을 클릭하세요 (예: BTS, 게임, 요리)")
            
            # 기본 검색 옵션
            st.subheader("검색 옵션")
            max_results = st.slider("최대 검색 결과", 10, 100, 50)
            order = st.selectbox("정렬 순서", 
                               ["relevance", "date", "viewCount", "rating", "viral_score"], 
                               format_func=lambda x: {
                                   "relevance": "관련도순",
                                   "date": "최신순", 
                                   "viewCount": "조회수순",
                                   "rating": "평점순",
                                   "viral_score": "바이럴 점수순"
                               }[x],
                               index=0)
            
            # 날짜 범위
            st.subheader("날짜 범위")
            date_range = st.selectbox("기간 선택", ["전체", "최근 1주일", "최근 1개월", "최근 6개월", "최근 1년", "사용자 정의"])
            
            # 사용자 정의 날짜 범위 (폼 내부로 이동)
            published_after = None
            published_before = None
            
            if date_range == "사용자 정의":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("시작일", value=datetime.now() - timedelta(days=30))
                    if start_date and not isinstance(start_date, tuple):
                        published_after = start_date.strftime("%Y-%m-%d")
                with col2:
                    end_date = st.date_input("종료일", value=datetime.now())
                    if end_date and not isinstance(end_date, tuple):
                        published_before = end_date.strftime("%Y-%m-%d")
            
            # 영상 길이 필터
            video_duration = st.selectbox("영상 길이", 
                                        ["전체", "short", "medium", "long"], 
                                        format_func=lambda x: {
                                            "전체": "모든 길이",
                                            "short": "4분 미만",
                                            "medium": "4-20분",
                                            "long": "20분 이상"
                                        }[x],
                                        index=0)
            
            # 검색 버튼
            search_clicked = st.form_submit_button("🔍 검색 시작", type="primary")
        
        # 날짜 범위 처리 (폼 외부에서 처리)
        if date_range == "최근 1주일":
            published_after = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif date_range == "최근 1개월":
            published_after = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif date_range == "최근 6개월":
            published_after = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        elif date_range == "최근 1년":
            published_after = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # 영상 길이 처리
        if video_duration == "전체":
            video_duration = None
    
    # 현재 검색 파라미터
    current_params = {
        'query': search_query,
        'max_results': max_results,
        'order': order,
        'date_range': date_range,
        'published_after': published_after,
        'published_before': published_before,
        'video_duration': video_duration
    }
    
    # 검색 실행 조건: 버튼 클릭 또는 파라미터 변경
    should_search = search_clicked and search_query
    
    # 메인 컨텐츠
    if should_search:
        # 검색 파라미터 저장
        st.session_state.last_search_params = current_params.copy()
        
        with st.spinner("YouTube 영상을 검색 중입니다..."):
            # YouTube API 검색
            collector = YouTubeDataCollector()
            api_order = order if order != "viral_score" else "relevance"  # API는 바이럴 점수 정렬을 지원하지 않으므로 관련도순으로 검색
            
            videos = collector.search_videos(
                query=search_query,
                max_results=max_results,
                order=api_order,
                published_after=published_after,
                published_before=published_before,
                video_duration=video_duration
            )
            
            if videos:
                st.session_state.search_results = videos
                st.session_state.current_order = order  # 현재 정렬 순서 저장
                
                # 검색 결과 요약 표시
                st.success(f"🎯 총 {len(videos)}개의 영상을 찾았습니다!")
                
                # 검색 조건 요약 표시
                search_summary = []
                if published_after:
                    if published_before:
                        search_summary.append(f"📅 기간: {published_after} ~ {published_before}")
                    else:
                        search_summary.append(f"📅 {published_after} 이후")
                if video_duration:
                    duration_text = {"short": "4분 미만", "medium": "4-20분", "long": "20분 이상"}[video_duration]
                    search_summary.append(f"⏱️ 영상 길이: {duration_text}")
                search_summary.append(f"📊 정렬: {order}")
                
                if search_summary:
                    st.info("🔍 검색 조건: " + " | ".join(search_summary))
                
                # 바이럴 분석 수행
                with st.spinner("바이럴 분석을 수행 중입니다..."):
                    analyzer = ViralAnalyzer()
                    keyword_analyzer = KeywordAnalyzer()
                    
                    # 각 영상에 대한 바이럴 분석
                    for video in videos:
                        # 채널 정보 가져오기
                        channel_info = collector.get_channel_info(video['channel_id'])
                        
                        # 바이럴 점수 계산
                        viral_analysis = analyzer.calculate_viral_score(video, channel_info)
                        video['viral_analysis'] = viral_analysis
                        video['channel_info'] = channel_info
                    
                    # 키워드 분석
                    keyword_analysis = keyword_analyzer.analyze_video_keywords(videos)
                    st.session_state.analysis_results = {
                        'keyword_analysis': keyword_analysis,
                        'trend_analysis': analyzer.analyze_trends(pd.DataFrame(videos))
                    }
                    
                    # 바이럴 점수순으로 정렬 (선택된 경우)
                    if order == "viral_score":
                        videos = sorted(videos, key=lambda x: x.get('viral_analysis', {}).get('viral_score', 0), reverse=True)
                        st.session_state.search_results = videos
                
                st.success("🎉 분석이 완료되었습니다!")
            else:
                st.error("❌ 검색 결과가 없습니다. 다른 키워드나 조건으로 시도해보세요.")
                st.info("💡 팁: 더 일반적인 키워드를 사용하거나 날짜 범위를 넓혀보세요.")
    
    # 기존 검색 결과 표시
    elif st.session_state.search_results:
        # 이전 검색 조건 표시
        if st.session_state.last_search_params:
            last_params = st.session_state.last_search_params
            st.info(f"🔍 마지막 검색: '{last_params.get('query', '')}' | {len(st.session_state.search_results)}개 결과")
        
        display_results()
    
    # 처음 접속한 경우 안내 메시지
    else:
        st.markdown("""
        ## 👋 YouTube 바이럴 영상 분석기에 오신 것을 환영합니다!
        
        ### 🚀 사용 방법:
        1. **왼쪽 사이드바**에서 검색 키워드를 입력하세요
        2. **검색 옵션**을 설정하세요 (결과 수, 정렬 방식, 날짜 범위 등)
        3. **🔍 검색 시작** 버튼을 클릭하세요
        4. 분석 결과를 확인하고 바이럴 영상을 찾아보세요!
        
        ### 📊 주요 기능:
        - **바이럴 점수 계산**: 독자적인 알고리즘으로 바이럴 가능성 측정
        - **키워드 분석**: 인기 키워드와 트렌드 분석
        - **상세 분석**: 조회수, 참여도, 채널 성과 등 종합 분석
        
        ---
        💡 **팁**: 'BTS', '게임', '요리', '뷰티' 등의 키워드로 시작해보세요!
        """)

def display_results():
    """검색 및 분석 결과를 표시합니다."""
    videos = st.session_state.search_results
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 영상 분석", "🔥 바이럴 영상", "🔍 키워드 분석", "📈 트렌드 분석"])
    
    with tab1:
        st.header("📊 영상 분석 결과")
        
        # 바이럴 영상 통계
        viral_videos = [v for v in videos if v.get('viral_analysis', {}).get('is_viral', False)]
        st.metric("바이럴 영상 수", len(viral_videos), f"{len(viral_videos)/len(videos)*100:.1f}%")
        
        # 영상 목록 표시 (정렬 순서 반영)
        display_videos = videos.copy()
        current_order = st.session_state.get('current_order', 'relevance')
        
        # 정렬 순서에 따라 영상 정렬
        if current_order == "viral_score":
            display_videos = sorted(display_videos, key=lambda x: x.get('viral_analysis', {}).get('viral_score', 0), reverse=True)
        elif current_order == "viewCount":
            display_videos = sorted(display_videos, key=lambda x: x.get('view_count', 0), reverse=True)
        elif current_order == "date":
            display_videos = sorted(display_videos, key=lambda x: x.get('published_at', ''), reverse=True)
        
        for i, video in enumerate(display_videos):
            with st.expander(f"🎬 {video['title'][:50]}...", expanded=i < 3):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 클릭 가능한 썸네일 링크
                    youtube_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                    st.markdown(f"""
                    <a href="{youtube_url}" target="_blank">
                        <img src="{video['thumbnail_url']}" width="200" style="border-radius: 8px; border: 2px solid #ddd; transition: border-color 0.3s;">
                    </a>
                    """, unsafe_allow_html=True)
                    st.markdown(f"[🎬 YouTube에서 보기]({youtube_url})", unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**채널:** {video['channel_title']}")
                    st.write(f"**조회수:** {video['view_count']:,}")
                    st.write(f"**좋아요:** {video['like_count']:,}")
                    st.write(f"**댓글:** {video['comment_count']:,}")
                    st.write(f"**게시일:** {video['published_at'][:10]}")
                    
                    if 'viral_analysis' in video:
                        viral_score = video['viral_analysis']['viral_score']
                        st.metric("바이럴 점수", f"{viral_score:.1f}/100")
                        
                        if video['viral_analysis']['is_viral']:
                            st.success("🔥 바이럴 영상!")
                        else:
                            st.info("📊 일반 영상")
    
    with tab2:
        st.header("🔥 바이럴 영상 순위")
        
        # 바이럴 점수 순으로 정렬
        sorted_videos = sorted(videos, key=lambda x: x.get('viral_analysis', {}).get('viral_score', 0), reverse=True)
        
        # 상위 10개 영상 표시
        for i, video in enumerate(sorted_videos[:10]):
            viral_analysis = video.get('viral_analysis', {})
            
            # 제목과 썸네일을 같은 줄에 배치
            col_thumb, col_title = st.columns([1, 3])
            
            with col_thumb:
                # 클릭 가능한 썸네일
                youtube_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                st.markdown(f"""
                <a href="{youtube_url}" target="_blank">
                    <img src="{video['thumbnail_url']}" width="120" style="border-radius: 8px; border: 2px solid #ff4444; transition: border-color 0.3s;">
                </a>
                """, unsafe_allow_html=True)
            
            with col_title:
                st.subheader(f"{i+1}. {video['title']}")
                st.markdown(f"[🎬 YouTube에서 보기]({youtube_url})")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("바이럴 점수", f"{viral_analysis.get('viral_score', 0):.1f}")
            with col2:
                st.metric("일일 조회수", f"{viral_analysis.get('views_per_day', 0):,.0f}")
            with col3:
                st.metric("좋아요 비율", f"{viral_analysis.get('like_ratio', 0):.2f}%")
            with col4:
                st.metric("댓글 비율", f"{viral_analysis.get('comment_ratio', 0):.2f}%")
            
            # 인사이트 표시
            if viral_analysis:
                analyzer = ViralAnalyzer()
                insights = analyzer.get_viral_insights(viral_analysis)
                for insight in insights:
                    st.write(f"• {insight}")
            
            st.markdown("---")
    
    with tab3:
        st.header("🔍 키워드 분석")
        
        if 'keyword_analysis' in st.session_state.analysis_results:
            keyword_analysis = st.session_state.analysis_results['keyword_analysis']
            
            # 키워드 인사이트
            keyword_analyzer = KeywordAnalyzer()
            insights = keyword_analyzer.get_keyword_insights(keyword_analysis)
            
            st.subheader("💡 키워드 인사이트")
            for insight in insights:
                st.write(f"• {insight}")
            
            # 워드클라우드 표시
            if keyword_analysis.get('combined_keywords'):
                st.subheader("☁️ 키워드 클라우드")
                try:
                    fig = keyword_analyzer.create_wordcloud(keyword_analysis['combined_keywords'])
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"워드클라우드 생성 중 오류: {e}")
            
            # 키워드 차트
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏷️ 인기 제목 키워드")
                if keyword_analysis.get('title_keywords'):
                    title_df = pd.DataFrame(keyword_analysis['title_keywords'], columns=['키워드', '빈도'])
                    st.bar_chart(title_df.set_index('키워드')['빈도'])
            
            with col2:
                st.subheader("📝 인기 태그")
                if keyword_analysis.get('top_tags'):
                    tag_df = pd.DataFrame(keyword_analysis['top_tags'], columns=['태그', '빈도'])
                    st.bar_chart(tag_df.set_index('태그')['빈도'])
    
    with tab4:
        st.header("📈 트렌드 분석")
        
        if videos:
            df = pd.DataFrame(videos)
            
            # 시간별 업로드 분포
            st.subheader("📅 업로드 시간 분포")
            df['published_date'] = pd.to_datetime(df['published_at'])
            df['hour'] = df['published_date'].dt.hour
            
            hourly_counts = df['hour'].value_counts().sort_index()
            st.bar_chart(hourly_counts)
            
            # 조회수 vs 바이럴 점수 산점도
            st.subheader("📊 조회수 vs 바이럴 점수")
            if 'viral_analysis' in df.columns:
                viral_scores = [v.get('viral_analysis', {}).get('viral_score', 0) for v in videos]
                scatter_df = pd.DataFrame({
                    '조회수': df['view_count'],
                    '바이럴 점수': viral_scores,
                    '제목': df['title']
                })
                
                fig = px.scatter(
                    scatter_df, 
                    x='조회수', 
                    y='바이럴 점수',
                    hover_data=['제목'],
                    title="조회수와 바이럴 점수의 상관관계"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 채널별 성과
            st.subheader("🎯 채널별 성과")
            channel_stats = df.groupby('channel_title').agg({
                'view_count': 'mean',
                'like_count': 'mean',
                'comment_count': 'mean'
            }).round(0)
            
            st.dataframe(channel_stats, use_container_width=True)

if __name__ == "__main__":
    main() 