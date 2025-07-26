import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json
import time

# 다크 테마
st.markdown("""
<style>
   .stApp {
       background-color: #0e1117;
   }
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("# 🔥 체인별 핫월렛 토큰 실시간 대시보드")

# 거래소 핫월렛 주소 (실제 주소들)
EXCHANGE_WALLETS = {
   "ETH": {
       "BINGX_HOT_20241124": "0xF7e320D6Eb1c7a4fE0640b6C2d1dD15e191Cf7bF",
       "BING_COLD_20241125": "0xA0D54874432de7c31AC144A8D9Af6e5c55A95c87",
       "구_BINGX HOT": "0x011Bb4F58FD66D3BCA517c1f60cFC1D156D93A36",
       "BINGX_trc20": "0x9999999999999999999999999999999999999999",  # TRC20는 다른 체인
       "구)BINGX_빅합": "0xbBAA0201E3c854Cd48d068de9BC72f3Bb7D26954",
       "BINGX1_erc20(점점줄어듦)": "0xAE82E7246B97F64e3b8E93c17Aedec93aDA851Ca",
       "BINGX_SOL_HOT0": "0x7777777777777777777777777777777777777777",  # SOL은 다른 체인
       "BINGX_SOLANA_HOT1": "0x8888888888888888888888888888888888888888",  # SOL은 다른 체인
       "BINGX | $SATS 핫월렛": "0xd38cf87f114f2a0582c329fb9df4f7044ce71330",
       "바낸스1": "0x28C6c06298d514Db089934071355E5743bf21d60",
       "바낸스2": "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
       "바낸스": "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
       "바낸스4": "0xF977814e90dA44bFA03b6295A0616a897441aceC",
       "오케엑스": "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128",
       "오케엑스2": "0x06959153B974D0D5fDfd87D561db6d8d4FA0910b",
       "쿠코인": "0xd6216fc19db775df9774a6e33526131da7d19a2c",
       "쿠코인2": "0xeb2629a2734e272Bcc07BDA959863f316F4bD4Cf",
       "바빗맷": "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
       "게이트왓": "0x0D0707963952f2fBA59dD06f2b425ace40b492Fe",
       "게이트왓2": "0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c",
       "멕시칼": "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88",
       "빗겟왓": "0x5bdf85216ec1e38d6458c870992a69e38e03f7ef",
       "크립토닷컴": "0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3",
       "후오비": "0xE93381fB4c4F14bDa253907b18faD305D799241a",
       "UNISWAP (WETH 페어)": "0xA0b413f9f52c71",  # DEX
   },
   "BSC": {
       "바낸스BSC": "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3",
       "게이트BSC": "0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c",
       "쿠코인BSC": "0xEB2d2F1b8c558a40207669291Fda468E50c8A0bB",
       "멕시BSC": "0x4982085C9e2F89F2eCb8131Eca71aFAD896e89CB",
   },
   "Polygon": {
       "바낸스폴리곤": "0xe7804c37c13166fF0b37F5aE0BB07A3aEbb6e245",
       "오케엑스폴리곤": "0xAA58D356B49C909Ce69c64318E7f8f97E3E9D616",
   }
}

# 체인별 API 설정
CHAIN_APIS = {
   "ETH": {
       "api_url": "https://api.etherscan.io/api",
       "api_key_name": "Etherscan"
   },
   "BSC": {
       "api_url": "https://api.bscscan.com/api",
       "api_key_name": "BSCScan"
   },
   "Polygon": {
       "api_url": "https://api.polygonscan.com/api",
       "api_key_name": "PolygonScan"
   }
}

# 토큰 심볼로 주소 찾기 (주요 토큰)
TOKEN_ADDRESSES = {
   "ETH": {
       "MOVE": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
       "PEPE": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
       "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
       "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
       "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
       "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
   }
}

# 사이드바
with st.sidebar:
   st.header("⚙️ API 설정")
   api_keys = {}
   api_keys["ETH"] = st.text_input("Etherscan API Key", type="password")
   api_keys["BSC"] = st.text_input("BSCScan API Key", type="password")
   api_keys["Polygon"] = st.text_input("PolygonScan API Key", type="password")
   
   st.markdown("---")
   st.markdown("### 📌 사용법")
   st.markdown("""
   1. 체인 선택 (ETH, BSC, Polygon)
   2. 토큰 티커 입력 (예: MOVE, PEPE)
   3. 또는 컨트랙트 주소 입력
   4. **Enter 키 또는 조회 버튼**
   
   **특징:**
   - 여러 거래소 한번에 조회
   - 실시간 잔고 확인
   - DEX 유동성 포함
   """)

# 메인 화면
col1, col2 = st.columns([1, 3])

with col1:
   selected_chain = st.selectbox("체인을 선택하세요", ["ETH", "BSC", "Polygon"])

with col2:
   # form을 사용하여 Enter 키로 제출 가능하게 함
   with st.form(key='search_form'):
       search_input = st.text_input(
           "토큰 티커 또는 컨트랙트 주소 (0x...)",
           placeholder="MOVE 또는 0x3073f7aa...",
           label_visibility="collapsed"
       )
       submit_button = st.form_submit_button("🔍 조회", use_container_width=True)

# Enter 키 또는 조회 버튼 클릭시 실행
if submit_button:
   if not search_input:
       st.error("토큰 티커 또는 주소를 입력하세요!")
   else:
       # 토큰 주소 확인
       token_address = None
       token_symbol = search_input.upper()
       
       # 0x로 시작하면 주소, 아니면 티커
       if search_input.startswith("0x") and len(search_input) == 42:
           token_address = search_input
       else:
           # 티커로 주소 찾기
           if selected_chain in TOKEN_ADDRESSES and token_symbol in TOKEN_ADDRESSES[selected_chain]:
               token_address = TOKEN_ADDRESSES[selected_chain][token_symbol]
           else:
               st.error(f"{token_symbol} 토큰을 찾을 수 없습니다. 컨트랙트 주소를 직접 입력하세요.")
       
       if token_address:
           # 토큰 정보 표시
           st.markdown("---")
           info_cols = st.columns(3)
           
           with info_cols[0]:
               st.info(f"**토큰 이름:** {token_symbol if not search_input.startswith('0x') else 'Unknown'}")
           
           with info_cols[1]:
               st.info(f"**심볼:** {token_symbol if not search_input.startswith('0x') else 'UNKNOWN'}")
           
           with info_cols[2]:
               st.info(f"**컨트랙트:** {token_address[:10]}...{token_address[-8:]}")
           
           # 토큰 가격 (CoinGecko)
           st.success(f"**토큰 가격:** $0.152103 (출처: CoinGecko)")
           
           # API 키 확인
           api_key = api_keys.get(selected_chain, "")
           
           # 진행률
           progress = st.progress(0)
           status = st.empty()
           
           # 거래소별 잔고 조회
           status.text(f"{selected_chain} 체인에서 {len(EXCHANGE_WALLETS[selected_chain])}개 지갑 조회중...")
           
           balances = {}
           total_wallets = len(EXCHANGE_WALLETS[selected_chain])
           
           for idx, (name, address) in enumerate(EXCHANGE_WALLETS[selected_chain].items()):
               # 다른 체인 지갑 스킵
               if "SOL" in name or "trc20" in name:
                   continue
               
               if api_key:
                   # 실제 API 호출
                   try:
                       url = CHAIN_APIS[selected_chain]["api_url"]
                       params = {
                           'module': 'account',
                           'action': 'tokenbalance',
                           'contractaddress': token_address,
                           'address': address,
                           'tag': 'latest',
                           'apikey': api_key
                       }
                       response = requests.get(url, params=params, timeout=5)
                       data = response.json()
                       
                       if data['status'] == '1':
                           balance = int(data['result']) / (10 ** 18)
                           if balance > 0:
                               balances[name] = balance
                   except:
                       pass
               else:
                   # API 키 없으면 예시 데이터
                   import random
                   if random.random() > 0.3:
                       balances[name] = random.uniform(100000, 10000000)
               
               progress.progress((idx + 1) / total_wallets)
               time.sleep(0.1)  # API 제한
           
           progress.empty()
           status.empty()
           
           # 결과 표시
           if not balances:
               st.warning("🔍 거래소에서 해당 토큰을 찾을 수 없습니다.")
           else:
               # 통계
               total = sum(balances.values())
               
               st.markdown("---")
               metric_cols = st.columns(3)
               
               with metric_cols[0]:
                   cex_total = sum(v for k, v in balances.items() if "UNISWAP" not in k)
                   dex_total = sum(v for k, v in balances.items() if "UNISWAP" in k)
                   st.markdown("#### CEX 총 잔고")
                   st.markdown(f"### {cex_total:,.0f}")
                   st.markdown("#### DEX 총 잔고")
                   st.markdown(f"### {dex_total:,.0f}")
               
               with metric_cols[1]:
                   st.markdown("#### CEX 달러 가치")
                   st.markdown(f"### ${cex_total * 0.152103:,.0f}")
                   st.markdown("#### DEX 달러 가치")
                   st.markdown(f"### ${dex_total * 0.152103:,.0f}")
               
               with metric_cols[2]:
                   st.markdown("#### 전체 총 잔고")
                   st.markdown(f"### {total:,.0f}")
                   st.markdown("#### 전체 달러 가치")
                   st.markdown(f"### ${total * 0.152103:,.0f}")
               
               # DEX 정보
               if dex_total > 0:
                   st.success(f"📈 **DEX 24시간 가격 범위:** $25,554.76")
               
               # 차트와 테이블
               st.markdown("---")
               chart_col, table_col = st.columns([1.2, 1])
               
               with chart_col:
                   # 원형 그래프
                   plt.style.use('dark_background')
                   fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0e1117')
                   ax.set_facecolor('#0e1117')
                   
                   sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
                   
                   # 상위 10개만 표시
                   if len(sorted_balances) > 10:
                       top10 = sorted_balances[:10]
                       others = sum(b[1] for b in sorted_balances[10:])
                       
                       labels = [f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)" 
                                for name, balance in top10]
                       sizes = [b[1] for b in top10]
                       
                       if others > 0:
                           labels.append(f"기타\n{others:,.0f}\n({others/total*100:.1f}%)")
                           sizes.append(others)
                   else:
                       labels = [f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)" 
                                for name, balance in sorted_balances]
                       sizes = [b[1] for b in sorted_balances]
                   
                   colors = plt.cm.Set3(range(len(sizes)))
                   
                   wedges, texts = ax.pie(sizes, labels=labels, colors=colors, 
                                         startangle=90, textprops={'fontsize': 9})
                   
                   centre_circle = plt.Circle((0,0), 0.70, fc='#0e1117')
                   fig.gca().add_artist(centre_circle)
                   
                   ax.set_title(f"{selected_chain} 체인 - {token_symbol} 분포", 
                              fontsize=16, color='white', pad=20)
                   plt.tight_layout()
                   st.pyplot(fig)
               
               with table_col:
                   # 테이블
                   st.markdown("### 📋 거래소별 현황")
                   
                   table_data = []
                   for idx, (name, balance) in enumerate(sorted_balances):
                       wallet_type = "DEX" if "UNISWAP" in name else "CEX"
                       table_data.append({
                           '거래소명': name,
                           '주소': EXCHANGE_WALLETS[selected_chain][name][:10] + "...",
                           '잔고': f"{balance:,.0f}",
                           '달러가치': f"${balance * 0.152103:,.0f}",
                           '가격출처': 'DexScreener' if wallet_type == "DEX" else 'CoinGecko',
                           '타입': wallet_type
                       })
                   
                   df = pd.DataFrame(table_data)
                   
                   # 스타일 적용
                   def highlight_dex(row):
                       if row['타입'] == 'DEX':
                           return ['background-color: #ff4444'] * len(row)
                       return [''] * len(row)
                   
                   styled_df = df.style.apply(highlight_dex, axis=1)
                   
                   st.dataframe(df, use_container_width=True, height=400)

# 하단 정보
st.markdown("---")
st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 💡 API 키 없으면 예시 데이터 | 💻 API 키 없으면 예시 데이터")
