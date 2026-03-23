import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 1. 설정: 추적할 상품 ID (무신사 주소창의 숫자)
PRODUCT_ID = "3364274" # 예시: 아디다스 가젤 등
URL = f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
CSV_FILE = "price_history.csv"

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 무신사 신규 레이아웃 대응 가격 추출
    price_text = soup.select_one(".product-detail__price-value").get_text()
    price = int(price_text.replace(',', '').replace('원', ''))
    return price

# 2. 데이터 업데이트
current_price = get_price()
today = datetime.now().strftime("%Y-%m-%d")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["date", "price"])

# 중복 날짜 방지 및 새 데이터 추가
if today not in df['date'].values:
    new_row = pd.DataFrame({"date": [today], "price": [current_price]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# 3. 그래프 생성
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['price'], marker='o', linestyle='-', color='b')
plt.title(f"Product {PRODUCT_ID} Price Trend")
plt.xlabel("Date")
plt.ylabel("Price (KRW)")
plt.xticks(rotation=45)
plt.grid(True, linestyle='--')
plt.tight_layout()
plt.savefig("price_chart.png")
