import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 1. 설정: 추적할 상품 ID
PRODUCT_ID = "5871994" 
URL = f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
CSV_FILE = "price_history.csv"

def get_price():
    # 무신사는 봇 차단이 강하므로 User-Agent 설정이 필수입니다.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 가격 정보 추출 (무신사 상품 페이지의 실시간 가격 태그)
    # 아래 선택자가 작동하지 않을 경우를 대비해 여러 시도를 합니다.
    price_tag = soup.select_one(".product-detail__price-value") or soup.select_one("#txt_price_member")
    
    if not price_tag:
        raise Exception("가격 정보를 찾을 수 없습니다. 상품 ID를 확인하거나 페이지 구조를 점검하세요.")
        
    price_text = price_tag.get_text(strip=True)
    price = int(price_text.replace(',', '').replace('원', ''))
    return price

try:
    # 2. 데이터 업데이트
    current_price = get_price()
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["date", "price"])

    if today not in df['date'].values:
        new_row = pd.DataFrame({"date": [today], "price": [current_price]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

    # 3. 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', linestyle='-', color='red')
    plt.title(f"Musinsa Product ({PRODUCT_ID}) Price Trend")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    print(f"성공: {today} 가격 {current_price}원 기록 완료")

except Exception as e:
    print(f"에러 발생: {e}")
    exit(1) # 에러 발생 시 GitHub Actions에 실패를 알림
