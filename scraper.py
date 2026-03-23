import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 상품 ID (무신사 주소창의 숫자)
PRODUCT_ID = "5871994" 
# 무신사 내부 데이터 API 주소 (보안이 더 낮고 정확함)
URL = f"https://goods-detail.musinsa.com/goods/{PRODUCT_ID}/v1/price"
CSV_FILE = "price_history.csv"

def get_price():
    # 실제 스마트폰에서 접속하는 것처럼 속이는 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Origin": "https://www.musinsa.com",
        "Referer": f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
    }
    
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code != 200:
        # 403 에러가 나면 다른 경로 시도
        raise Exception(f"무신사 차단 발생 (상태코드: {response.status_code})")
    
    data = response.json()
    # 무신사 API 구조에서 판매가(salePrice) 추출
    price = data.get('data', {}).get('prices', {}).get('salePrice')
    
    if not price:
        raise Exception("가격 데이터를 찾을 수 없습니다.")
    return int(price)

try:
    current_price = get_price()
    today = datetime.now().strftime("%Y-%m-%d")

    # 데이터 저장 로직
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["date", "price"])

    if today not in df['date'].values:
        new_row = pd.DataFrame({"date": [today], "price": [current_price]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', color='royalblue', linewidth=2)
    plt.title(f"Item {PRODUCT_ID} Price Trend", fontsize=15)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    
    print(f"✅ 성공! 오늘의 가격: {current_price}원")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
