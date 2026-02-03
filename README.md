# 📈🐜 AntKstockTramingCamp(개미국장훈련소)🏕️
투자 초보들이 실제 매매 전 전략을 검증하고 투자 감각을 기를 수 있도록 설계한 자동화 분석 프로젝트입니다.  
투자의 기초적인 지표인 이동평균선, MACD, 볼린저 밴드 기반의 전략 모듈을 분리하여 주가를 분석합니다.

스케쥴러를 사용하여 매일 관심종목의 종가를 자동으로 수집- 분석하여 매도/매수 추천 알림을 보내드립니다.  

알고리즘이 추천하는 대로 가상자산을 운영해보세요  

투자에 대한 감각을 키우실 수 있습니다.

※ 향후에는 자동 매매까지 구현하여 이용자의 자산을 운영하는 자동시스템까지 고도화할 예정입니다.  
이용자가 원하는 매매 기준을 입력하면 그 기준에 따라 자동으로 투자하는 시스템 구현을 목표로 하고 있습니다.

## Key Features
 - 스케줄러 기반 자동 주식 데이터 수집 및 전처리
 - 전략 기반 매수/매도 로직 및 추천 알림
 - 전략 기반 투자 이력관리

## Development Milestones
- Phase 1: 종가 수집 및 DB저장 자동화
- Phase 2: 주가 분석 자동화
- Phase 3: 매도/매수 추천 및 알림 시스템
- Phase 4: 계좌 잔액 계산 및 포트폴리오 관리
- Phase 5: 주가 분석 후보 종목 선정 로직

## Tech Stack
### Backend
- Python  
  - 데이터 수집, 분석 로직 및 전체 비즈니스 로직 구현
- FastAPI  
  - 주가 분석 결과 및 추천 정보를 제공하는 API 서버

### Data Processing & Analysis
- pandas  
  - 주가 데이터 전처리 및 지표 계산
 
### Database
- MySQL  
  - 수집된 종가 데이터, 분석 결과, 투자 이력 저장
- SQLAlchemy  
  - ORM 기반 데이터베이스 모델링 및 접근
    
### Scheduling
- APScheduler  
  - 장 마감 후 종가 데이터 자동 수집 및 분석 스케줄링

### Notification
- Discord Webhook  
  - 매수/매도 추천 결과 실시간 알림 전송

### Infrastructure
- Docker  
  - 개발 및 실행 환경 통일
- Docker Compose  
  - API 서버 및 데이터베이스 구성 관리

### Environment & Configuration
- Pydantic  
  - 환경 변수 및 요청 데이터 검증
- python-dotenv  
  - 환경 변수 관리


## Architecture
<img width="974" height="683" alt="image" src="https://github.com/user-attachments/assets/988586b9-a973-460d-b040-dbf140a43ec7" />

## ERD
<img width="787" height="798" alt="image" src="https://github.com/user-attachments/assets/74a191b4-65a4-4a51-a7fa-273f28a704b5" />

## Directory Structure
AntKstockTrainingCamp/
├── app/
│   ├── core/
│   │   └── database/                             // DB 세션 설정값 정의
│   ├── price_data/                               // 초기 데이터 적재를 위한 종가 데이터파일 (삭제예정)
│   │   └── ........... 
│   ├── scripts/                                  // 시스템 개발 중 테스트 스크립트 및 초기 데이터 크롤링 스크립트 (1차 개발 완료 시 삭제 예정)
│   │   ├── crawling_prices.py                    
│   │   ├── load_csv.py                           
│   │   ├── load_stock_metadata.py                
│   │   ├── load_watchlist.py                     
│   │   ├── make_table.py                         
│   │   ├── prices_to_DB.py                      
│   │   ├── restAPI_test.py                       
│   │   └── test.py                               
│   ├── service/                                  // **시스템 비즈니스 레이어**
│   │   ├── analysis.py                           // 종가 기반으로 투자 지표 계산 및 DB 저장
│   │   ├── collector.py                          // 종가 수집
│   │   ├── notify.py                             // 매매 추천 알림
│   │   ├── recommend.py                          // 투자 지표 기반 매매 조건 판별
│   │   ├── scanner.py                            // 관심 종목 중 추천 후보 조건 판별
│   │   └── trade_manager.py                      // 매매 시 포트폴리오 데이터 반영 및 거래 금액 계좌 데이터 반영 
│   └── utils/
│       └── templates.py                          // 추천 알림 템플릿 
├── data_0233_20251108.csv                        //  주식 메타데이터 (삭제예정)
├── etf_data_1606_20251123.csv                    //  etf 메타데이터 (삭제예정)
├── main.py                                       // 스케줄링 및 서비스 루틴
├── model.py                                      // 데이터베이스 테이블 구조 정의
├── schemas.py                                    // 요청·응답 및 도메인 데이터 구조 정의
└── README.md

## Future Improvements
◻ 투자 전략 추가하여 전략별 수익률 비교  
◻ 추천에 따른 자동 매매  
◻ **최종 목표** : GCP(Google Cloud Platform) 24시간 배포 -> 스케쥴링을 통한 모든 시스템 자동화
