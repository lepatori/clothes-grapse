import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 상품 ID (숫자만 입력)
PRODUCT_ID = "5871994" 
# 무신사 내부 모바일 데이터 주소 (이 경로는 보안 검사가 훨씬 유연합니다)
URL = f"https://goods-detail.musinsa.com/goods/{PRODUCT_ID}/v1/price"
CSV_FILE = "price_history.csv"

def get_price():
    # 아이폰 앱에서 접속하는 것처럼 정교하게 속입니다.
    headers = {
        "User-Agent": "Musinsa/APP (iPhone; iOS 17.4; ko_KR)",
        "Accept": "application/json",
        "x-musinsa-app-version": "1.0.0",
        "Referer": f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
    }
    
    response = requests.get(URL, headers=headers, timeout=20)
    
    # 만약 여기서도 403이 나면, 일반 웹 경로가 아닌 다른 API를 시도합니다.
    if response.status_code != 200:
        print(f"DEBUG: API 접속 실패({response.status_code}). 대안 경로 시도 중...")
        # 대안 경로 (검색 결과용 API)
        alt_url = f"https://search.musinsa.com/api/v1/goods/{PRODUCT_ID}"
        response = requests.get(alt_url, headers=headers, timeout=20)
        
    if response.status_code == 200:
        data = response.json()
        # API 구조에 따라 가격 위치가 다를 수 있으므로 안전하게 추출
        try:
            price = data['data']['prices']['salePrice']
        except:
            price = data.get('price') or data.get('salePrice')
            
        if price:
            return int(price)
            
    raise Exception(f"모든 경로 차단됨 (마지막 코드: {response.status_code})")

try:
    current_price = get_price()
    today = datetime.now().strftime("%Y-%m-%d")

    # 데이터 저장
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["date", "price"])

    # 오늘 날짜 없으면 추가
    if today not in df['date'].values:
        new_row = pd.DataFrame({"date": [today], "price": [current_price]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

    # 그래프 생성 (파란색 테마)
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', color='#007AFF', linewidth=3)
    plt.title(f"Musinsa Price Tracker - {PRODUCT_ID}", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Price (KRW)")
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    
    print(f"🎯 기적적으로 성공! {today} 가격: {current_price}원")

except Exception as e:
    print(f"❌ {e}")
    exit(1)
