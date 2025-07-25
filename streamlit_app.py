import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# 제목
st.title("🔍 토큰별 거래소 잔고 추적기")

# 거래소 핫월렛 주소 (실제 주소들)
EXCHANGE_WALLETS = {
   "Binance": {
       "주소": ["0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance 14
               "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",  # Binance 15
               "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",  # Binance 16
               "0xF977814e90dA44bFA03b6295A0616a897441aceC",  # Binance 8
               "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"],  # Binance 1
       "타입": "CEX"
   },
   "OKX": {
       "주소": ["0x06959153B974D0D5fDfd87D561db6d8d4FA0910b",  # OKX 6
               "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128"],  # OKX 10
       "타입": "CEX"
   },
   "Bitget": {
       "주소": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],  # 실제 Bitget 주소
       "타입": "CEX"
   },
   "MEXC": {
       "주소": ["0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88"],  # 실제 MEXC 주소
       "타입": "CEX"
   },
   "BingX": {
       "주소": ["0xd38cf87f114f2a0582c329fb9df4f7044ce71330"],  # 실제 BingX 주소
       "타입": "CEX"
   },
   "Gate.io": {
       "주소": ["0x0D0707963952f2fBA59dD06f2b425ace40b492Fe",  # Gate.io 1
               "0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c"],  # Gate.io 2
       "타입": "CEX"
   },
   "KuCoin": {
       "주소": ["0xeb2629a2734e272Bcc07BDA959863f316F4bD4Cf",  # KuCoin 5
               "0xd6216fc19db775df9774a6e33526131da7d19a2c"],  # KuCoin 6
       "타입": "CEX"
   },
   "Crypto.com": {
       "주소": ["0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3",  # Crypto.com 1
               "0x46340b20830761efd32832A74d7169B29FEB9758"],  # Crypto.com 2
       "타입": "CEX"
   },
   "Huobi": {
       "주소": ["0xE93381fB4c4F14bDa253907b18faD305D799241a",  # Huobi 10
               "0x18709E89BD403F470088aBDAcEbE86CC60dda12e"],  # Huobi 34
       "타입": "CEX"
   },
   "Bybit": {
       "주소": ["0xf89d7b9c864f589bbF53a82105107622B35EaA40"],  # Bybit 1
       "타입": "CEX"
   }
}

# 인기 토큰 정보 (체인 정보 포함)
TOKENS = {
   "MOVE": {
       "address": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
       "chains": ["ERC-20"],
       "price": 0.152103,
       "price_change": "+12.34%"
   },
   "PEPE": {
       "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
       "chains": ["ERC-20"],
       "price": 0.00001234,
       "price_change": "-5.67%"
   },
   "SHIB": {
       "address": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
       "chains": ["ERC-20", "BSC"],
       "price": 0.00000892,
       "price_change": "+2.45%"
   },
   "MATIC": {
       "address": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
       "chains": ["ERC-20", "Polygon"],
       "price": 0.8521,
       "price_change": "+8.92%"
   }
}

# 토큰 선택
selected_token = st.selectbox("토큰 선택", list(TOKENS.keys()))
token_info = TOKENS[selected_token]

# 토큰 정보 표시
col1, col2 = st.columns(2)
with col1:
   st.write(f"**현재가:** ${token_info['price']:.8f}")
   delta_color = "green" if token_info['price_change'].startswith('+') else "red"
   st.markdown(f"**24h 변동:** <span style='color:{delta_color}'>{token_info['price_change']}</span>", unsafe_allow_html=True)

with col2:
   chains_text = " / ".join(token_info['chains'])
   st.write(f"**토큰 주소 ({chains_text}):**")
   st.code(token_info['address'], language=None)

if st.button("🔍 조회하기", type="primary"):
   # 구분선
   st.markdown("---")
   
   # 예시 데이터 (실제로는 블록체인에서 가져와야 함)
   if selected_token == "MOVE":
       balances = {
           "Binance": 59724591.91,
           "OKX": 9754106.01,
           "Bitget": 5847293.12,
           "MEXC": 3129670.32,
           "BingX": 1987654.43,
           "Gate.io": 884020.71,
           "KuCoin": 205700.75,
           "Crypto.com": 523421.32,
           "Huobi": 342156.78,
           "Bybit": 987234.56
       }
   else:
       # 다른 토큰은 임의 데이터
       import random
       balances = {k: random.uniform(100000, 10000000) for k in EXCHANGE_WALLETS.keys()}
   
   # 총 잔고 계산
   total = sum(balances.values())
   
   # 메트릭 표시
   col1, col2, col3, col4 = st.columns(4)
   
   with col1:
       st.metric("전체 보유량", f"{total:,.0f}")
   
   with col2:
       st.metric("달러 가치", f"${total * token_info['price']:,.2f}")
   
   with col3:
       st.metric("거래소 수", len(balances))
   
   with col4:
       top3_percent = sum(sorted(balances.values(), reverse=True)[:3]) / total * 100
       st.metric("상위 3개 집중도", f"{top3_percent:.1f}%")
   
   # 원형 그래프와 테이블을 나란히 배치
   st.markdown("---")
   col1, col2 = st.columns([1, 1])
   
   with col1:
       st.subheader("📊 거래소별 분포")
       
       # 원형 그래프 생성
       fig, ax = plt.subplots(figsize=(10, 8))
       
       # 상위 5개 거래소만 표시하고 나머지는 '기타'로
       sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
       top5 = sorted_balances[:5]
       others_sum = sum([b[1] for b in sorted_balances[5:]])
       
       labels = [f"{b[0]}\n{b[1]:,.0f}\n({b[1]/total*100:.1f}%)" for b in top5]
       if others_sum > 0:
           labels.append(f"기타\n{others_sum:,.0f}\n({others_sum/total*100:.1f}%)")
       
       sizes = [b[1] for b in top5]
       if others_sum > 0:
           sizes.append(others_sum)
       
       colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
       
       wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='',
                                         startangle=90, textprops={'fontsize': 10})
       
       # 도넛 모양으로 만들기
       centre_circle = plt.Circle((0,0), 0.70, fc='white')
       fig.gca().add_artist(centre_circle)
       
       ax.axis('equal')
       plt.tight_layout()
       st.pyplot(fig)
   
   with col2:
       st.subheader("📋 거래소별 현황")
       
       # 테이블 생성
       data = []
       for exchange, balance in sorted(balances.items(), key=lambda x: x[1], reverse=True):
           main_address = EXCHANGE_WALLETS[exchange]["주소"][0]
           data.append({
               '거래소': exchange,
               '잔고': f"{balance:,.0f}",
               '점유율': f"{balance/total*100:.2f}%",
               '주소': main_address[:10] + "..." + main_address[-6:]
           })
       
       df = pd.DataFrame(data)
       st.dataframe(df, use_container_width=True, height=400)
   
   # 인사이트
   st.markdown("---")
   st.subheader("💡 주요 인사이트")
   
   col1, col2 = st.columns(2)
   
   with col1:
       top_exchange = max(balances.items(), key=lambda x: x[1])
       st.info(f"""
       **시장 집중도 분석**
       - {top_exchange[0]}가 전체의 {top_exchange[1]/total*100:.1f}% 보유 (최다)
       - 상위 3개 거래소가 {sum(sorted(balances.values(), reverse=True)[:3])/total*100:.1f}% 차지
       - 상위 5개 거래소가 {sum(sorted(balances.values(), reverse=True)[:5])/total*100:.1f}% 차지
       """)
   
   with col2:
       avg_balance = sum(balances.values()) / len(balances)
       st.info(f"""
       **분포 특성**
       - 평균 보유량: {avg_balance:,.0f}
       - 최대/최소 비율: {max(balances.values())/min(balances.values()):.1f}x
       - 10개 거래소에 분산 보관 중
       """)

# 정보
st.markdown("---")
st.caption("💡 거래소 주소는 Etherscan에서 확인된 실제 주소입니다. 블록체인 데이터는 예시값입니다.")
st.caption("📍 실제 구현시 Web3 또는 Etherscan API로 실시간 잔고를 조회합니다.")
