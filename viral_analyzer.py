"""
바이럴 영상 판별 및 분석 모듈
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

class ViralAnalyzer:
    def __init__(self):
        self.thresholds = config.VIRAL_THRESHOLDS
    
    def calculate_viral_score(self, video_data, channel_data=None):
        """
        영상의 바이럴 점수를 계산합니다.
        
        Args:
            video_data (dict): 영상 데이터
            channel_data (dict): 채널 데이터 (선택사항)
        
        Returns:
            dict: 바이럴 점수 및 세부 지표
        """
        # 게시일로부터 경과 일수 계산
        published_date = datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00'))
        days_since_published = (datetime.now().replace(tzinfo=published_date.tzinfo) - published_date).days
        days_since_published = max(1, days_since_published)  # 최소 1일
        
        # 기본 지표 계산
        views_per_day = video_data['view_count'] / days_since_published
        like_ratio = video_data['like_count'] / max(video_data['view_count'], 1)
        comment_ratio = video_data['comment_count'] / max(video_data['view_count'], 1)
        
        # 참여도 점수 계산
        engagement_score = (video_data['like_count'] + video_data['comment_count'] * 5) / max(video_data['view_count'], 1) * 10000
        
        # 채널 대비 성과 (채널 정보가 있는 경우)
        channel_performance_ratio = 1.0
        if channel_data and channel_data.get('subscriber_count', 0) > 0:
            expected_views = channel_data['subscriber_count'] * 0.1  # 구독자의 10%가 봤을 것으로 예상
            channel_performance_ratio = video_data['view_count'] / max(expected_views, 1)
        
        # 바이럴 점수 계산 (0-100점)
        score_components = {
            'views_per_day_score': min(views_per_day / self.thresholds['views_per_day'] * 25, 25),
            'like_ratio_score': min(like_ratio / self.thresholds['like_ratio'] * 25, 25),
            'comment_ratio_score': min(comment_ratio / self.thresholds['comment_ratio'] * 25, 25),
            'engagement_score': min(engagement_score / self.thresholds['engagement_score'] * 25, 25)
        }
        
        viral_score = sum(score_components.values())
        
        # 채널 성과 보너스 (최대 20점 추가)
        if channel_performance_ratio > 2:
            viral_score += min(20, (channel_performance_ratio - 1) * 5)
        
        viral_score = min(100, viral_score)
        
        return {
            'viral_score': round(viral_score, 2),
            'views_per_day': round(views_per_day, 2),
            'like_ratio': round(like_ratio * 100, 4),  # 퍼센트로 표시
            'comment_ratio': round(comment_ratio * 100, 4),  # 퍼센트로 표시
            'engagement_score': round(engagement_score, 2),
            'channel_performance_ratio': round(channel_performance_ratio, 2),
            'days_since_published': days_since_published,
            'is_viral': viral_score >= 70,  # 70점 이상을 바이럴로 판정
            'score_components': score_components
        }
    
    def analyze_trends(self, videos_df):
        """
        영상들의 트렌드를 분석합니다.
        
        Args:
            videos_df (pd.DataFrame): 영상 데이터프레임
        
        Returns:
            dict: 트렌드 분석 결과
        """
        if videos_df.empty:
            return {}
        
        # 날짜별 분석
        videos_df['published_date'] = pd.to_datetime(videos_df['published_at'])
        videos_df['published_day'] = videos_df['published_date'].dt.day_name()
        videos_df['published_hour'] = videos_df['published_date'].dt.hour
        
        # 요일별 평균 조회수
        daily_avg_views = videos_df.groupby('published_day')['view_count'].mean().sort_values(ascending=False)
        
        # 시간대별 평균 조회수
        hourly_avg_views = videos_df.groupby('published_hour')['view_count'].mean().sort_values(ascending=False)
        
        # 카테고리별 분석
        category_stats = videos_df.groupby('category_id').agg({
            'view_count': ['mean', 'count'],
            'like_count': 'mean',
            'comment_count': 'mean'
        }).round(2)
        
        return {
            'daily_trends': daily_avg_views.to_dict(),
            'hourly_trends': hourly_avg_views.to_dict(),
            'category_stats': category_stats.to_dict(),
            'total_videos': len(videos_df),
            'avg_views': videos_df['view_count'].mean(),
            'top_performing_day': daily_avg_views.index[0] if len(daily_avg_views) > 0 else None,
            'optimal_upload_hour': hourly_avg_views.index[0] if len(hourly_avg_views) > 0 else None
        }
    
    def get_viral_insights(self, video_analysis):
        """
        바이럴 점수 분석 결과를 바탕으로 인사이트를 제공합니다.
        
        Args:
            video_analysis (dict): 영상 바이럴 분석 결과
        
        Returns:
            list: 인사이트 텍스트 리스트
        """
        insights = []
        
        if video_analysis['is_viral']:
            insights.append("🔥 이 영상은 바이럴 영상으로 판정됩니다!")
        else:
            insights.append("📊 이 영상은 일반적인 성과를 보이고 있습니다.")
        
        # 조회수 성과 분석
        if video_analysis['views_per_day'] > self.thresholds['views_per_day']:
            insights.append(f"👀 일일 평균 조회수가 {video_analysis['views_per_day']:,.0f}회로 매우 높습니다!")
        elif video_analysis['views_per_day'] > self.thresholds['views_per_day'] * 0.5:
            insights.append(f"📈 일일 평균 조회수가 {video_analysis['views_per_day']:,.0f}회로 준수한 편입니다.")
        else:
            insights.append(f"📉 일일 평균 조회수가 {video_analysis['views_per_day']:,.0f}회로 개선이 필요합니다.")
        
        # 참여도 분석
        if video_analysis['like_ratio'] > self.thresholds['like_ratio'] * 100:
            insights.append(f"👍 좋아요 비율이 {video_analysis['like_ratio']:.2f}%로 높은 호응을 받고 있습니다!")
        
        if video_analysis['comment_ratio'] > self.thresholds['comment_ratio'] * 100:
            insights.append(f"💬 댓글 비율이 {video_analysis['comment_ratio']:.2f}%로 활발한 소통이 이루어지고 있습니다!")
        
        # 채널 성과 분석
        if video_analysis['channel_performance_ratio'] > 2:
            insights.append(f"🚀 채널 평균 대비 {video_analysis['channel_performance_ratio']:.1f}배 높은 성과를 보이고 있습니다!")
        elif video_analysis['channel_performance_ratio'] < 0.5:
            insights.append("💡 채널 평균 대비 낮은 성과입니다. 제목이나 썸네일 개선을 고려해보세요.")
        
        return insights
    
    def predict_viral_potential(self, video_data, hours_since_upload=24):
        """
        초기 데이터를 바탕으로 바이럴 가능성을 예측합니다.
        
        Args:
            video_data (dict): 영상 데이터
            hours_since_upload (int): 업로드 후 경과 시간
        
        Returns:
            dict: 바이럴 가능성 예측 결과
        """
        if hours_since_upload < 1:
            return {"prediction": "분석하기에는 시간이 부족합니다."}
        
        # 시간당 성장률 계산
        views_per_hour = video_data['view_count'] / hours_since_upload
        likes_per_hour = video_data['like_count'] / hours_since_upload
        comments_per_hour = video_data['comment_count'] / hours_since_upload
        
        # 24시간 후 예상 수치
        predicted_24h_views = views_per_hour * 24
        predicted_24h_engagement = (likes_per_hour + comments_per_hour * 5) * 24
        
        # 바이럴 가능성 점수 (0-100)
        potential_score = 0
        
        if predicted_24h_views > self.thresholds['views_per_day']:
            potential_score += 40
        elif predicted_24h_views > self.thresholds['views_per_day'] * 0.5:
            potential_score += 20
        
        if predicted_24h_engagement > 1000:
            potential_score += 30
        elif predicted_24h_engagement > 500:
            potential_score += 15
        
        # 초기 성장률 보너스
        if hours_since_upload <= 6 and views_per_hour > 1000:
            potential_score += 30
        
        potential_score = min(100, potential_score)
        
        return {
            'viral_potential_score': potential_score,
            'predicted_24h_views': round(predicted_24h_views),
            'predicted_24h_engagement': round(predicted_24h_engagement),
            'current_growth_rate': round(views_per_hour, 2),
            'recommendation': self.get_growth_recommendation(potential_score)
        }
    
    def get_growth_recommendation(self, potential_score):
        """
        성장 가능성 점수에 따른 추천사항을 제공합니다.
        """
        if potential_score >= 80:
            return "🚀 매우 높은 바이럴 가능성! 추가 프로모션을 고려해보세요."
        elif potential_score >= 60:
            return "📈 좋은 성장세입니다. SNS 공유를 늘려보세요."
        elif potential_score >= 40:
            return "💡 보통 수준입니다. 썸네일이나 제목 최적화를 고려해보세요."
        else:
            return "📊 성장이 더딘 상태입니다. 컨텐츠 전략 재검토가 필요할 수 있습니다." 