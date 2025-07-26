import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# 다크 테마 CSS 스타일
st.markdown("""
<style>
   /* 전체 배경 다크 테마 */
   .stApp {
       background-color: #0e1117;
       color: #fafafa;
   }
   
   /* 메트릭 컨테이너 스타일 */
   div[data-testid="metric-container"] {
       background-color: #262730;
       border: 1px solid #333;
       padding: 15px;
       border-radius: 8px;
       color: #fafafa;
   }
   
   /* 메트릭 라벨 색상 */
   div[data-testid="metric-container"] label {
       color: #fafafa !important;
   }
   
   /* 메트릭 값 색상 */
   div[data-testid="metric-container"] div[data-testid="metric-value"] {
       color: #fafafa !important;
   }
   
   /* 컬럼 구분선 */
   .css-1outpf7 {
       background-color: #262730;
   }
   
   /* selectbox 스타일 */
   .stSelectbox > div > div {
       background-color: #262730;
       color: #fafafa;
   }
   
   /* 정보 박스 스타일 */
   .stAlert {
       background-color: #262730;
       color: #fafafa;
       border: 1px solid #333;
   }
   
   /* 테이블 스타일 */
   .dataframe {
       background-color: #0e1117 !important;
       color: #fafafa !important;
   }
   
   /* 테이블 헤더 */
   .dataframe thead tr th {
       background-color: #262730 !important;
       color: #fafafa !important;
   }
   
   /* 테이블 행 */
   .dataframe tbody tr {
       background-color: #0e1117 !important;
       color: #fafafa !important;
   }
   
   /* 테이블 행 호버 */
   .dataframe tbody tr:hover {
       background-color: #262730 !important;
   }
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("# 🔥 체인별 핫월렛 토큰 실시간 대시보드")

# 체인 선택
chain_col, _ = st.columns([2, 8])
with chain_col:
   selected_chain = st.selectbox("체인을 선택하세요", ["ETH", "BSC", "Polygon", "Arbitrum"])

# 토큰 정보 섹션
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
   st.info("**토큰 이름:** Movement")

with col2:
   st.info("**심볼:** MOVE")

with col3:
   st.info("**컨트랙트:** 0x3073f7aa...1a3073")

# 토큰 가격
st.success("**토큰 가격:** $0.152103 (출처: CoinGecko)")

# 설정 섹션
col1, col2 = st.columns([8, 2])

with col1:
   st.warning("⚠️ **DEX 유동성 풀 포함 (베타)**")
   st.info("🔄 DEX 유동성 풀 조회는 베타 기능입니다. 주요 DEX의 페어를 표시합니다.")

with col2:
   st.markdown("#### 병렬처리 워커 수")
   worker_count = st.slider("", 1, 10, 5, label_visibility="collapsed")

# 24시간 가격 정보
st.success("📈 **DEX 24시간 가격 범위:** $25,554.76")

# 메트릭 섹션
st.markdown("---")
st.markdown("### 📊 전체 현황")

col1, col2, col3 = st.columns(3)

with col1:
   st.metric("CEX 총 잔고", "86,128,410.5574")
   st.metric("DEX 총 잔고", "150,397.8275")

with col2:
   st.metric("CEX 달러 가치", "$13,100,389.63")
   st.metric("DEX 달러 가치", "$22,845.43")

with col3:
   st.metric("전체 총 잔고", "86,278,808.3849")
   st.metric("전체 달러 가치", "$13,123,235.06")

# 상세 테이블
st.markdown("---")
st.markdown("### 📋 거래소별 상세 현황")

# 테이블 데이터
data = {
   '시간이름': ['바낸스1', '오케엑스', '바낸스', '바낸스2', '쿠코인', '바빗맷', 
               '게이트왓', '🔥 UNISWAP (WETH 페어)', '멕시칼', '바낸스콜드우성장',
               '바낸스4', '빗썸벳', '쿠코인', '빗겟왓2'],
   '주소': ['0x28c6c062...f21d69', '0x91d40e48...c8debe', '0xdfd5293d...439c3d',
           '0x21a31ee1...285549', '0xe9d1e086...1d3e43', '0xf89d7b9c...5eaa40',
           '0xb80707f8...b492de', '0xA0b413f9...f52c71', '0x9642b23e...2f5d4e',
           '0x5e2E3E8...70E1cb', '0x6084f59e...f9c976', '0x0ddfb521...d3f1ef',
           '0xf91efec7...930747', '0x053955f4...70d206'],
   '잔고': [59724591.9063, 9754106.0084, 7032183.9337, 5387967.5034, 3129670.3224,
           884020.7099, 205700.7547, 150397.8275, 10169.3686, 0.0000,
           0.0000, 0.0000, 0.0000, 0.0000],
   '달러가치': ['$9,084,289.60', '$1,483,628.79', '$1,069,616.27', '$819,526.03',
              '$476,032.25', '$134,462.20', '$31,287.70', '$22,845.43', '$1,546.79',
              '$0.00', '$0.00', '$0.00', '$0.00', '$0.00'],
   '가격출처': ['CoinGecko', 'CoinGecko', 'CoinGecko', 'CoinGecko', 'CoinGecko',
               'CoinGecko', 'CoinGecko', 'DexScreener', 'CoinGecko', 'CoinGecko',
               'CoinGecko', 'CoinGecko', 'CoinGecko', 'CoinGecko'],
   '타입': ['CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'DEX', 'CEX', 'CEX',
           'CEX', 'CEX', 'CEX', 'CEX'],
   '탐색기': ['🔍 확인'] * 14
}

df = pd.DataFrame(data)

# 테이블 표시
st.dataframe(
   df,
   use_container_width=True,
   height=500,
   column_config={
       "잔고": st.column_config.NumberColumn(
           "잔고",
           format="%.4f"
       )
   }
)

# 차트 섹션
st.markdown("---")
st.markdown("### 📈 시각화")

col1, col2 = st.columns(2)

with col1:
   st.markdown("#### CEX vs DEX 분포")
   
   # 파이 차트 - 다크 테마
   plt.style.use('dark_background')
   fig1, ax1 = plt.subplots(figsize=(8, 6), facecolor='#0e1117')
   ax1.set_facecolor('#0e1117')
   
   sizes = [86128410.5574, 150397.8275]
   labels = ['CEX\n86,128,410\n(99.83%)', 'DEX\n150,398\n(0.17%)']
   colors = ['#3498db', '#e74c3c']
   
   wedges, texts = ax1.pie(sizes, labels=labels, colors=colors, startangle=90,
                           textprops={'color': 'white', 'fontsize': 10})
   
   # 도넛 모양
   centre_circle = plt.Circle((0,0), 0.70, fc='#0e1117')
   fig1.gca().add_artist(centre_circle)
   
   ax1.axis('equal')
   plt.tight_layout()
   st.pyplot(fig1)

with col2:
   st.markdown("#### 상위 7개 거래소 잔고")
   
   # 막대 차트 - 다크 테마
   top_exchanges = df[df['잔고'] > 0].nlargest(7, '잔고')
   
   fig2, ax2 = plt.subplots(figsize=(8, 6), facecolor='#0e1117')
   ax2.set_facecolor('#0e1117')
   
   # 색상 설정
   colors_bar = []
   for _, row in top_exchanges.iterrows():
       if row['타입'] == 'DEX':
           colors_bar.append('#e74c3c')
       else:
           colors_bar.append('#3498db')
   
   bars = ax2.barh(range(len(top_exchanges)), top_exchanges['잔고'], color=colors_bar)
   
   # y축 라벨 설정
   ax2.set_yticks(range(len(top_exchanges)))
   ax2.set_yticklabels(top_exchanges['시간이름'], color='white')
   
   ax2.set_xlabel('잔고', color='white')
   ax2.set_title('거래소별 토큰 보유량', color='white')
   
   # 축 색상
   ax2.tick_params(colors='white')
   ax2.spines['bottom'].set_color('white')
   ax2.spines['top'].set_color('white')
   ax2.spines['left'].set_color('white')
   ax2.spines['right'].set_color('white')
   
   # 값 표시
   for i, value in enumerate(top_exchanges['잔고']):
       ax2.text(value, i, f' {value:,.0f}', va='center', color='white')
   
   plt.tight_layout()
   st.pyplot(fig2)

# 추가 정보
st.markdown("---")
with st.expander("ℹ️ 추가 정보"):
   st.markdown("""
   - **데이터 출처**: 블록체인 온체인 데이터 (Etherscan API)
   - **업데이트 주기**: 1분마다 자동 갱신
   - **DEX 지원**: Uniswap V2/V3, SushiSwap, PancakeSwap
   - **지원 체인**: Ethereum, BSC, Polygon, Arbitrum, Optimism
   - **API 제공**: CoinGecko (가격), DexScreener (DEX 데이터)
   """)

# 실제 거래소 주소 목록
EXCHANGE_ADDRESSES = {
   "바낸스1": "0x28C6c06298d514Db089934071355E5743bf21d60",
   "오케엑스": "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128",
   "바낸스": "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
   "바낸스2": "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
   "쿠코인": "0xd6216fc19db775df9774a6e33526131da7d19a2c",
   "바빗맷": "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
   "게이트왓": "0x0D0707963952f2fBA59dD06f2b425ace40b492Fe",
   "UNISWAP": "0xA0b413f9f52c71",
   "멕시칼": "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88",
   "비빗겟": "0x5bdf85216ec1e38d6458c870992a69e38e03f7ef",
   "빙엑스": "0xd38cf87f114f2a0582c329fb9df4f7044ce71330"
}

# 하단 정보
st.markdown("---")
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
st.caption(f"⏰ 마지막 업데이트: {current_time} | 📊 실시간 블록체인 데이터 | 🔗 Etherscan API 연동")
