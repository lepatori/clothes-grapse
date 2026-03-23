import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 상품 ID를 입력하세요 (예: 3364274)
PRODUCT_ID = "5871994" 
URL = f"https://www.musinsa.com/app/goods/{PRODUCT_ID}"
CSV_FILE = "price_history.csv"

def get_price():
    # 2026년 브라우저 기준의 헤더 설정 (중요!)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    response = requests.get(URL, headers=headers, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"접속 실패 (상태코드: {response.status_code})")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 무신사 최신 가격 태그 (class 이름이 자주 바뀔 수 있으므로 여러 개 지정)
    selectors = [
        ".product-detail__price-value", 
        "#txt_price_member", 
        ".product_title_price",
        "span.price"
    ]
    
    price_tag = None
    for selector in selectors:
        price_tag = soup.select_one(selector)
        if price_tag:
            break
            
    if not price_tag:
        raise Exception("가격을 찾을 수 없습니다. 무신사 페이지 구조가 변경되었을 수 있습니다.")
        
    # 숫자만 추출
    price_text = price_tag.get_text()
    price = int(''.join(filter(str.isdigit, price_text)))
    return price

try:
    # 데이터 처리
    current_price = get_price()
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["date", "price"])

    # 오늘 데이터가 없으면 추가
    if today not in df['date'].values:
        new_data = pd.DataFrame({"date": [today], "price": [current_price]})
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

    # 그래프 생성 (한글 깨짐 방지를 위해 영어 제목 사용)
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['price'], marker='s', color='black', linewidth=2)
    plt.title(f"Price History for Item {PRODUCT_ID}")
    plt.xlabel("Date")
    plt.ylabel("Price (KRW)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    
    print(f"Success: {today} - {current_price}원")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
