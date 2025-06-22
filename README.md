# 📺 YouTube 바이럴 영상 분석기

Python과 Streamlit을 활용하여 YouTube 바이럴 영상을 검색하고 분석하는 웹 애플리케이션입니다.

## 🚀 주요 기능

### 1. 영상 검색 및 수집
- YouTube Data API v3를 활용한 고도화된 검색
- 다양한 필터링 옵션 (날짜, 영상 길이, 정렬 방식)
- 영상 메타데이터 자동 수집 (조회수, 좋아요, 댓글 등)

### 2. 바이럴 영상 판별 시스템
- 독자적인 바이럴 점수 계산 알고리즘
- 일일 조회수, 참여도, 채널 성과 등 다면적 분석
- 실시간 바이럴 가능성 예측

### 3. 키워드 분석
- 제목, 설명, 태그에서 핵심 키워드 추출
- 한국어/영어 자동 언어 감지 및 처리
- 워드클라우드 시각화
- 트렌드 키워드 분석

### 4. 시각화 및 대시보드
- 인터랙티브 차트 및 그래프
- 영상별 상세 분석 결과
- 채널별 성과 비교
- 트렌드 분석 대시보드

## 📋 요구사항

- Python 3.8 이상
- YouTube Data API v3 키

## 🛠️ 설치 방법

1. **저장소 클론**
```bash
git clone <repository-url>
cd youtube_filter
```

2. **가상환경 생성 (권장)**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **NLTK 데이터 다운로드 (선택사항)**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
```

## 🔑 API 키 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. YouTube Data API v3 활성화
3. API 키 발급
4. `config.py` 파일에서 `YOUTUBE_API_KEY` 값 수정

## 🎯 실행 방법

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`으로 접속하여 사용할 수 있습니다.

## 📊 사용법

### 1. 기본 검색
1. 사이드바에서 검색 키워드 입력
2. 검색 옵션 설정 (결과 수, 정렬 방식, 날짜 범위 등)
3. "🔍 검색 시작" 버튼 클릭

### 2. 분석 결과 확인
- **영상 분석**: 전체 영상 목록과 기본 통계
- **바이럴 영상**: 바이럴 점수 순으로 정렬된 상위 영상들
- **키워드 분석**: 핵심 키워드 추출 및 워드클라우드
- **트렌드 분석**: 시간별, 채널별 트렌드 분석

### 3. 고급 기능
- 사용자 정의 날짜 범위 설정
- 영상 길이별 필터링
- 채널별 성과 비교
- 키워드 트렌드 분석

## 🧮 바이럴 점수 계산 방식

바이럴 점수는 다음 요소들을 종합하여 0-100점으로 계산됩니다:

- **일일 조회수** (25점): 게시일 대비 조회수 성장률
- **좋아요 비율** (25점): 조회수 대비 좋아요 비율
- **댓글 비율** (25점): 조회수 대비 댓글 비율
- **참여도 점수** (25점): 전체적인 사용자 참여도
- **채널 성과 보너스** (최대 20점): 채널 평균 대비 성과

70점 이상의 영상을 바이럴 영상으로 판정합니다.

## 📈 기술 스택

- **Backend**: Python 3.8+
- **Frontend**: Streamlit
- **API**: YouTube Data API v3
- **데이터 처리**: Pandas, NumPy
- **시각화**: Plotly, Matplotlib, WordCloud
- **텍스트 분석**: NLTK, KoNLPy (선택)

## 🔧 구성 파일

- `config.py`: API 키 및 설정값 관리
- `youtube_api.py`: YouTube API 연동 모듈
- `viral_analyzer.py`: 바이럴 분석 로직
- `keyword_analyzer.py`: 키워드 분석 기능
- `app.py`: Streamlit 메인 애플리케이션

## ⚠️ 주의사항

1. **API 할당량**: YouTube API는 일일 할당량이 있습니다. 과도한 요청 시 제한될 수 있습니다.
2. **라이브러리 설치**: 일부 텍스트 분석 라이브러리(KoNLPy)는 추가 시스템 의존성이 필요할 수 있습니다.
3. **API 키 보안**: API 키를 공개 저장소에 업로드하지 마세요.

## 🎨 커스터마이징

### 바이럴 판별 기준 변경
`config.py`의 `VIRAL_THRESHOLDS` 값을 수정하여 바이럴 판별 기준을 조정할 수 있습니다.

### 키워드 분석 언어 추가
`keyword_analyzer.py`에서 언어별 처리 로직을 추가할 수 있습니다.

### UI 테마 변경
Streamlit의 테마 설정을 통해 UI를 커스터마이징할 수 있습니다.

## 📞 문의 및 지원

프로젝트 사용 중 문제가 발생하거나 기능 개선 제안이 있으시면 이슈를 등록해 주세요.

---

**Made with ❤️ using Python & Streamlit** 