"""
키워드 추출 및 분석 모듈
"""

import re
import pandas as pd
import numpy as np
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import config

# matplotlib 한글 폰트 설정
try:
    # Windows
    if 'malgun' in [f.name.lower() for f in fm.fontManager.ttflist]:
        plt.rcParams['font.family'] = 'Malgun Gothic'
    # macOS
    elif 'applesd gothic neo' in [f.name.lower() for f in fm.fontManager.ttflist]:
        plt.rcParams['font.family'] = 'AppleSD Gothic Neo'  
    # 기본값
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
except:
    pass

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False

class KeywordAnalyzer:
    def __init__(self):
        self.korean_stopwords = set(config.STOPWORDS_KO)
        if NLTK_AVAILABLE:
            self.english_stopwords = set(stopwords.words('english')).union(set(config.STOPWORDS_EN))
        else:
            self.english_stopwords = set(config.STOPWORDS_EN)
        
        if KONLPY_AVAILABLE:
            self.okt = Okt()
        else:
            self.okt = None
    
    def extract_keywords_from_text(self, text, language='auto', max_keywords=20):
        """
        텍스트에서 키워드를 추출합니다.
        
        Args:
            text (str): 분석할 텍스트
            language (str): 언어 ('ko', 'en', 'auto')
            max_keywords (int): 최대 키워드 수
        
        Returns:
            list: (키워드, 빈도) 튜플 리스트
        """
        if not text or not isinstance(text, str):
            return []
        
        # 언어 자동 감지
        if language == 'auto':
            language = self.detect_language(text)
        
        if language == 'ko' and self.okt:
            keywords = self.extract_korean_keywords(text, max_keywords)
        else:
            keywords = self.extract_english_keywords(text, max_keywords)
        
        return keywords
    
    def detect_language(self, text):
        """
        텍스트의 언어를 감지합니다.
        
        Args:
            text (str): 분석할 텍스트
        
        Returns:
            str: 'ko' 또는 'en'
        """
        # 한글 문자 비율 계산
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))
        
        if total_chars == 0:
            return 'en'
        
        korean_ratio = korean_chars / total_chars
        return 'ko' if korean_ratio > 0.3 else 'en'
    
    def extract_korean_keywords(self, text, max_keywords=20):
        """
        한국어 텍스트에서 키워드를 추출합니다.
        """
        if not self.okt:
            return self.extract_simple_keywords(text, max_keywords)
        
        try:
            # 형태소 분석
            morphs = self.okt.morphs(text, stem=True)
            
            # 명사만 추출
            nouns = self.okt.nouns(text)
            
            # 불용어 제거 및 고급 필터링
            filtered_words = [
                word for word in nouns 
                if (len(word) > 1 and 
                    word not in self.korean_stopwords and
                    not word.isdigit() and
                    not self.is_url_fragment(word.lower()) and
                    not self.is_meaningless_word(word.lower()))
            ]
            
            # 빈도 계산
            word_freq = Counter(filtered_words)
            
            return word_freq.most_common(max_keywords)
            
        except Exception as e:
            print(f"한국어 키워드 추출 오류: {e}")
            return self.extract_simple_keywords(text, max_keywords)
    
    def extract_english_keywords(self, text, max_keywords=20):
        """
        영어 텍스트에서 키워드를 추출합니다.
        """
        if not NLTK_AVAILABLE:
            return self.extract_simple_keywords(text, max_keywords)
        
        try:
            # 토큰화
            tokens = word_tokenize(text.lower())
            
            # 품사 태깅
            pos_tags = pos_tag(tokens)
            
            # 명사와 형용사만 추출 (고급 필터링 적용)
            keywords = [
                word for word, pos in pos_tags
                if (pos.startswith(('NN', 'JJ')) and len(word) > 2
                    and word not in self.english_stopwords
                    and word.isalpha()
                    and not self.is_url_fragment(word.lower())
                    and not self.is_meaningless_word(word.lower()))
            ]
            
            # 빈도 계산
            word_freq = Counter(keywords)
            
            return word_freq.most_common(max_keywords)
            
        except Exception as e:
            print(f"영어 키워드 추출 오류: {e}")
            return self.extract_simple_keywords(text, max_keywords)
    
    def extract_simple_keywords(self, text, max_keywords=20):
        """
        간단한 키워드 추출 (라이브러리 없이)
        """
        # URL 패턴 제거
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.[\w.-]+\.\w+', '', text)
        
        # 텍스트 정리 (한글, 영문, 숫자만 유지)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        words = text.split()
        
        # 고급 필터링
        filtered_words = []
        for word in words:
            word_lower = word.lower()
            # 길이, 숫자, 불용어 필터링
            if (len(word) > 2 and 
                not word.isdigit() and 
                not word_lower in self.korean_stopwords and 
                not word_lower in self.english_stopwords and
                not self.is_url_fragment(word_lower) and
                not self.is_meaningless_word(word_lower)):
                filtered_words.append(word_lower)
        
        # 빈도 계산
        word_freq = Counter(filtered_words)
        
        return word_freq.most_common(max_keywords)
    
    def is_url_fragment(self, word):
        """URL 조각인지 확인"""
        url_patterns = [
            r'^www',
            r'\.com$',
            r'\.net$',
            r'\.org$',
            r'\.kr$',
            r'\.co$',
            r'^http',
            r'^https',
            r'youtube',
            r'youtu\.be'
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, word):
                return True
        return False
    
    def is_meaningless_word(self, word):
        """의미 없는 단어인지 확인"""
        # 연속된 같은 문자 (ㅋㅋㅋ, ㅎㅎㅎ 등)
        if re.match(r'^(.)\1{2,}$', word):
            return True
        
        # 특수문자만 포함된 단어
        if re.match(r'^[^\w가-힣]+$', word):
            return True
        
        # 너무 짧거나 긴 단어
        if len(word) < 2 or len(word) > 20:
            return True
            
        return False
    
    def analyze_video_keywords(self, videos_data):
        """
        여러 영상의 키워드를 종합 분석합니다.
        
        Args:
            videos_data (list): 영상 데이터 리스트
        
        Returns:
            dict: 키워드 분석 결과
        """
        all_titles = []
        all_descriptions = []
        all_tags = []
        
        for video in videos_data:
            all_titles.append(video.get('title', ''))
            all_descriptions.append(video.get('description', ''))
            if video.get('tags'):
                all_tags.extend(video['tags'])
        
        # 제목 키워드 분석
        title_text = ' '.join(all_titles)
        title_keywords = self.extract_keywords_from_text(title_text, max_keywords=30)
        
        # 설명 키워드 분석
        description_text = ' '.join(all_descriptions)
        description_keywords = self.extract_keywords_from_text(description_text, max_keywords=30)
        
        # 태그 빈도 분석
        tag_freq = Counter(all_tags)
        top_tags = tag_freq.most_common(20)
        
        # 전체 키워드 통합
        all_keywords = {}
        for keyword, freq in title_keywords:
            all_keywords[keyword] = all_keywords.get(keyword, 0) + freq * 3  # 제목 가중치 3배
        
        for keyword, freq in description_keywords:
            all_keywords[keyword] = all_keywords.get(keyword, 0) + freq
        
        for tag, freq in top_tags:
            all_keywords[tag] = all_keywords.get(tag, 0) + freq * 2  # 태그 가중치 2배
        
        # 상위 키워드 선별
        top_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:50]
        
        return {
            'title_keywords': title_keywords,
            'description_keywords': description_keywords,
            'top_tags': top_tags,
            'combined_keywords': top_keywords,
            'total_videos_analyzed': len(videos_data)
        }
    
    def create_wordcloud(self, keywords_freq, width=400, height=200, 
                        background_color='white', max_words=50):
        """
        키워드로 워드클라우드를 생성합니다.
        
        Args:
            keywords_freq (list): (키워드, 빈도) 튜플 리스트
            width (int): 워드클라우드 너비
            height (int): 워드클라우드 높이
            background_color (str): 배경색
            max_words (int): 최대 단어 수
        
        Returns:
            matplotlib.figure.Figure: 워드클라우드 그림
        """
        if not keywords_freq:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.text(0.5, 0.5, '키워드가 없습니다', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # 키워드 딕셔너리 생성
        keyword_dict = dict(keywords_freq)
        
        # 한글 폰트 경로 찾기
        try:
            from font_utils import get_wordcloud_font_path
            font_path = get_wordcloud_font_path()
        except Exception as e:
            print(f"폰트 경로 가져오기 실패: {e}")
            font_path = None
        
        # 워드클라우드 생성 시도
        wordcloud_params = {
            'width': width,
            'height': height,
            'background_color': background_color,
            'max_words': max_words,
            'relative_scaling': 0.5,
            'min_font_size': 8,
            'colormap': 'viridis'
        }
        
        # 폰트가 있으면 추가
        if font_path:
            wordcloud_params['font_path'] = font_path
        
        try:
            # 워드클라우드 생성
            wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(keyword_dict)
            
            # 그래프 생성
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            
            return fig
            
        except Exception as e:
            print(f"워드클라우드 생성 오류: {e}")
            
            # 폰트 없이 다시 시도
            try:
                if 'font_path' in wordcloud_params:
                    del wordcloud_params['font_path']
                wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(keyword_dict)
                
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                
                print("⚠️ 한글 폰트 없이 워드클라우드를 생성했습니다.")
                return fig
                
            except Exception as e2:
                print(f"폰트 없는 워드클라우드 생성도 실패: {e2}")
                
                # 최종 대체: 텍스트 리스트로 표시
                fig, ax = plt.subplots(figsize=(6, 3))
                
                # 상위 키워드들을 텍스트로 표시
                top_keywords = list(keyword_dict.keys())[:10]
                keyword_text = ", ".join(top_keywords)
                
                ax.text(0.5, 0.5, f'주요 키워드:\n{keyword_text}', 
                       ha='center', va='center', fontsize=10, 
                       transform=ax.transAxes, wrap=True)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('키워드 분석 결과')
                
                return fig
    
    def analyze_keyword_trends(self, videos_data, time_period='daily'):
        """
        시간별 키워드 트렌드를 분석합니다.
        
        Args:
            videos_data (list): 영상 데이터 리스트
            time_period (str): 분석 기간 ('daily', 'weekly', 'monthly')
        
        Returns:
            dict: 트렌드 분석 결과
        """
        if not videos_data:
            return {}
        
        # 날짜별로 영상 그룹화
        videos_df = pd.DataFrame(videos_data)
        videos_df['published_date'] = pd.to_datetime(videos_df['published_at'])
        
        if time_period == 'daily':
            videos_df['time_group'] = videos_df['published_date'].dt.date
        elif time_period == 'weekly':
            videos_df['time_group'] = videos_df['published_date'].dt.to_period('W')
        else:  # monthly
            videos_df['time_group'] = videos_df['published_date'].dt.to_period('M')
        
        # 시간대별 키워드 분석
        trend_data = {}
        for time_group, group_data in videos_df.groupby('time_group'):
            group_videos = group_data.to_dict('records')
            keywords_analysis = self.analyze_video_keywords(group_videos)
            trend_data[str(time_group)] = keywords_analysis['combined_keywords'][:10]
        
        return trend_data
    
    def get_keyword_insights(self, keyword_analysis):
        """
        키워드 분석 결과에서 인사이트를 추출합니다.
        
        Args:
            keyword_analysis (dict): 키워드 분석 결과
        
        Returns:
            list: 인사이트 리스트
        """
        insights = []
        
        if not keyword_analysis.get('combined_keywords'):
            return ["분석할 키워드가 없습니다."]
        
        top_keywords = keyword_analysis['combined_keywords'][:5]
        insights.append(f"🔍 가장 인기 있는 키워드: {', '.join([kw[0] for kw in top_keywords])}")
        
        # 제목과 설명에서 공통으로 나타나는 키워드 찾기
        title_kw = set([kw[0] for kw in keyword_analysis['title_keywords'][:10]])
        desc_kw = set([kw[0] for kw in keyword_analysis['description_keywords'][:10]])
        common_kw = title_kw.intersection(desc_kw)
        
        if common_kw:
            insights.append(f"💡 제목과 설명에 공통으로 사용되는 핵심 키워드: {', '.join(list(common_kw)[:3])}")
        
        # 태그 활용도 분석
        if keyword_analysis.get('top_tags'):
            avg_tag_freq = sum([freq for _, freq in keyword_analysis['top_tags']]) / len(keyword_analysis['top_tags'])
            insights.append(f"🏷️ 평균 태그 사용 빈도: {avg_tag_freq:.1f}회")
        
        return insights
    
 