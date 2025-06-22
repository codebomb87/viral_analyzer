"""
YouTube API를 사용한 데이터 수집 모듈
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta
import config

class YouTubeDataCollector:
    def __init__(self):
        self.api_key = config.YOUTUBE_API_KEY
        self.youtube = build(
            config.YOUTUBE_API_SERVICE_NAME,
            config.YOUTUBE_API_VERSION,
            developerKey=self.api_key
        )
    
    def search_videos(self, query, max_results=50, order='relevance', 
                     published_after=None, published_before=None, 
                     video_duration=None, region_code='KR'):
        """
        YouTube에서 영상을 검색합니다.
        
        Args:
            query (str): 검색 키워드
            max_results (int): 최대 결과 수
            order (str): 정렬 순서 (relevance, date, rating, viewCount, title)
            published_after (str): 검색 시작 날짜 (YYYY-MM-DD)
            published_before (str): 검색 종료 날짜 (YYYY-MM-DD)
            video_duration (str): 영상 길이 (short, medium, long)
            region_code (str): 지역 코드
        
        Returns:
            list: 검색된 영상 정보 리스트
        """
        try:
            search_params = {
                'part': 'id,snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'order': order,
                'regionCode': region_code
            }
            
            if published_after:
                search_params['publishedAfter'] = f"{published_after}T00:00:00Z"
            if published_before:
                search_params['publishedBefore'] = f"{published_before}T23:59:59Z"
            if video_duration:
                search_params['videoDuration'] = video_duration
            
            search_response = self.youtube.search().list(**search_params).execute()
            
            video_ids = []
            for item in search_response['items']:
                video_ids.append(item['id']['videoId'])
            
            # 영상 상세 정보 가져오기
            videos_info = self.get_video_details(video_ids)
            
            return videos_info
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return []
    
    def get_video_details(self, video_ids):
        """
        영상 ID 리스트로부터 상세 정보를 가져옵니다.
        
        Args:
            video_ids (list): 영상 ID 리스트
        
        Returns:
            list: 영상 상세 정보 리스트
        """
        try:
            videos_response = self.youtube.videos().list(
                part='id,snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            videos_info = []
            for item in videos_response['items']:
                video_info = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'tags': item['snippet'].get('tags', []),
                    'category_id': item['snippet']['categoryId'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'duration': item['contentDetails']['duration'],
                    'thumbnail_url': item['snippet']['thumbnails']['medium']['url']
                }
                videos_info.append(video_info)
            
            return videos_info
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return []
    
    def get_channel_info(self, channel_id):
        """
        채널 정보를 가져옵니다.
        
        Args:
            channel_id (str): 채널 ID
        
        Returns:
            dict: 채널 정보
        """
        try:
            channel_response = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            if channel_response['items']:
                item = channel_response['items'][0]
                return {
                    'channel_id': item['id'],
                    'channel_title': item['snippet']['title'],
                    'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                    'video_count': int(item['statistics'].get('videoCount', 0)),
                    'view_count': int(item['statistics'].get('viewCount', 0))
                }
            return {}
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return {}
    
    def get_video_comments(self, video_id, max_results=100):
        """
        영상의 댓글을 가져옵니다.
        
        Args:
            video_id (str): 영상 ID
            max_results (int): 최대 댓글 수
        
        Returns:
            list: 댓글 리스트
        """
        try:
            comments_response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            ).execute()
            
            comments = []
            for item in comments_response['items']:
                comment = {
                    'comment_id': item['id'],
                    'text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                    'author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'like_count': item['snippet']['topLevelComment']['snippet']['likeCount'],
                    'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt']
                }
                comments.append(comment)
            
            return comments
            
        except HttpError as e:
            print(f"댓글 가져오기 오류: {e}")
            return []
    
    def parse_duration(self, duration_str):
        """
        ISO 8601 형식의 duration을 초 단위로 변환합니다.
        
        Args:
            duration_str (str): ISO 8601 형식의 duration (예: PT4M13S)
        
        Returns:
            int: 초 단위 시간
        """
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds 