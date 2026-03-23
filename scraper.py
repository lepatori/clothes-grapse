import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re

# 사용자가 입력한 상품 ID: 5871994
PRODUCT_ID = "5871994" 
URL = f"https://www.musinsa.com/products/{PRODUCT_ID}" # 2026년형 최신 주소 체계
CSV_FILE = "price_history.csv"

def get_price():
    # 구글 검색 봇(Googlebot)으로 완벽하게 위장합니다.
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Cache-Control": "no-cache"
    }
    
    response = requests.get(URL, headers=headers, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"무신사 접속 거부 (상태코드: {response.status_code})")
    
    # HTML 내에서 가격 데이터 추출 (정규표현식 사용)
    # 태그 구조가 바뀌어도 소스 코드 내의 숫자 데이터를 직접 찾아냅/니다.
    html_content = response.text
    
    # "price": 12345 형태나 "salePrice": 12345 형태를 모두 찾습니다.
    price_match = re.search(r'"price":\s*(\d+)', html_content) or \
                  re.search(r'"salePrice":\s*(\d+)', html_content) or \
                  re.search(r'"currentPrice":\s*(\d+)', html_content)
    
    if price_match:
        return int(price_match.group(1))
        
    # 만약 정규식으로 못 찾으면 마지막 수단으로 태그 분석
    soup = BeautifulSoup(html_content, 'html.parser')
    price_tag = soup.select_one(".product-detail__price-value")
    if price_tag:
        return int(re.sub(r'[^0-9]', '', price_tag.get_text()))
        
    raise Exception("가격 데이터를 찾을 수 없습니다. (ID 확인 필요)")

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

    # 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='s', color='green', linewidth=2)
    plt.title(f"Musinsa Price Tracker (ID: {PRODUCT_ID})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    
    print(f"✅ 드디어 뚫었습니다! 오늘의 가격: {current_price}원")

except Exception as e:
    print(f"❌ {e}")
    exit(1)
