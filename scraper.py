import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 상품 ID를 확인하세요! (예: 가젤 3364274)
PRODUCT_ID = "5871994" 
URL = f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
CSV_FILE = "price_history.csv"

def get_price():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    res = requests.get(URL, headers=headers)
    
    if res.status_code != 200:
        raise Exception(f"페이지 접속 실패! 상태코드: {res.status_code}")
        
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 무신사 가격 태그 후보들 (구조 변경 대비)
    price_tag = soup.select_one(".product-detail__price-value") or \
                soup.select_one("#txt_price_member") or \
                soup.select_one(".product_title_price")
    
    if not price_tag:
        # 디버깅을 위해 HTML 일부 출력 (로그에서 확인 가능)
        print(res.text[:500]) 
        raise Exception("가격 태그를 찾을 수 없습니다.")
        
    price_text = price_tag.get_text(strip=True)
    # 숫자만 남기기
    price = int(''.join(filter(str.isdigit, price_text)))
    return price

try:
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

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', color='blue')
    plt.title(f"Price Trend (ID: {PRODUCT_ID})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    print(f"성공! {today} 가격: {current_price}")

except Exception as e:
    print(f"에러 발생: {e}")
    exit(1)
