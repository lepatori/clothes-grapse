import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 상품 ID (무신사 주소창의 숫자)
PRODUCT_ID = "5871994" 
URL = f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
CSV_FILE = "price_history.csv"

def get_price():
    # 2026년 최신 브라우저 환경을 완벽하게 흉내냅니다.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    
    # 세션을 사용해 쿠키를 자동으로 관리하게 합니다.
    session = requests.Session()
    response = session.get(URL, headers=headers, timeout=20)
    
    if response.status_code != 200:
        raise Exception(f"접속 실패 (코드: {response.status_code})")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 가격을 찾는 3단계 필터링 (무신사의 다양한 레이아웃 대응)
    price = None
    
    # 1순위: 메인 가격 태그
    tag = soup.select_one(".product-detail__price-value") or \
          soup.select_one("#txt_price_member") or \
          soup.select_one(".is-price")
    
    if tag:
        price_text = tag.get_text(strip=True)
        price = int(''.join(filter(str.isdigit, price_text)))
    else:
        # 2순위: 페이지 내 스크립트 데이터에서 찾기 (JSON 형태)
        import re
        price_match = re.search(r'"price":(\d+)', response.text)
        if price_match:
            price = int(price_match.group(1))

    if not price:
        raise Exception("가격 데이터를 찾을 수 없습니다. (구조 변경 가능성)")
    return price

try:
    current_price = get_price()
    today = datetime.now().strftime("%Y-%m-%d")

    # 데이터 저장 및 그래프 생성
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["date", "price"])

    if today not in df['date'].values:
        new_row = pd.DataFrame({"date": [today], "price": [current_price]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', color='#ff0000', linewidth=2) # 강렬한 빨간색 그래프
    plt.title(f"Musinsa Price Tracker (ID: {PRODUCT_ID})")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    
    print(f"🎉 드디어 성공! {today} 가격: {current_price}원")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
