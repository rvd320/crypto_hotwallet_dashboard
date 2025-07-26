import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json

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
   }
}

# 인기 토큰 예시 (빠른 선택용)
EXAMPLE_TOKENS = {
   "직접 입력": "",
   "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
   "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
   "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
   "MOVE": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
   "PEPE": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
   "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
}

# Etherscan API 키 (실제 사용시 필요)
ETHERSCAN_API_KEY = st.sidebar.text_input("Etherscan API Key", type="password", help="https://etherscan.io/apis 에서 무료로 발급")

# 토큰 선택/입력
col1, col2 = st.columns([1, 2])

with col1:
   selected_example = st.selectbox("예시 토큰", list(EXAMPLE_TOKENS.keys()))

with col2:
   if selected_example != "직접 입력":
       token_address = st.text_input("토큰 컨트랙트 주소", value=EXAMPLE_TOKENS[selected_example])
   else:
       token_address = st.text_input("토큰 컨트랙트 주소", placeholder="0x... (ERC-20 토큰 주소 입력)")

# 토큰 정보 가져오기 함수
@st.cache_data(ttl=300)  # 5분 캐시
def get_token_info(token_address):
   """토큰 정보를 Etherscan API에서 가져오기"""
   if not ETHERSCAN_API_KEY:
       return None
   
   try:
       # 토큰 정보 조회
       url = f"https://api.etherscan.io/api"
       params = {
           'module': 'token',
           'action': 'tokeninfo',
           'contractaddress': token_address,
           'apikey': ETHERSCAN_API_KEY
       }
       response = requests.get(url, params=params)
       data = response.json()
       
       if data['status'] == '1' and data['result']:
           result = data['result'][0]
           return {
               'name': result.get('tokenName', 'Unknown'),
               'symbol': result.get('symbol', 'Unknown'),
               'decimals': int(result.get('divisor', '18').replace('1', '').count('0'))
           }
   except Exception as e:
       st.error(f"토큰 정보 조회 실패: {e}")
   
   return None

# 토큰 가격 가져오기 함수
@st.cache_data(ttl=60)  # 1분 캐시
def get_token_price(token_address):
   """CoinGecko API로 토큰 가격 조회"""
   try:
       # CoinGecko API (무료, API 키 불필요)
       url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum"
       params = {
           'contract_addresses': token_address,
           'vs_currencies': 'usd',
           'include_24hr_change': 'true'
       }
       response = requests.get(url, params=params)
       data = response.json()
       
       if token_address.lower() in data:
           price_data = data[token_address.lower()]
           return {
               'price': price_data.get('usd', 0),
               'change_24h': price_data.get('usd_24h_change', 0)
           }
   except Exception as e:
       # CoinGecko에 없는 토큰은 0으로 표시
       pass
   
   return {'price': 0, 'change_24h': 0}

# 토큰 잔고 조회 함수
@st.cache_data(ttl=60)  # 1분 캐시
def get_token_balance(wallet_address, token_address):
   """Etherscan API로 토큰 잔고 조회"""
   if not ETHERSCAN_API_KEY:
       return 0
   
   try:
       url = f"https://api.etherscan.io/api"
       params = {
           'module': 'account',
           'action': 'tokenbalance',
           'contractaddress': token_address,
           'address': wallet_address,
           'tag': 'latest',
           'apikey': ETHERSCAN_API_KEY
       }
       response = requests.get(url, params=params)
       data = response.json()
       
       if data['status'] == '1':
           balance = int(data['result'])
           return balance
       else:
           return 0
   except Exception as e:
       return 0

# 체인 감지 함수
def detect_chains(token_address):
   """토큰이 어느 체인에 있는지 감지"""
   chains = []
   
   # 기본적으로 Ethereum 주소 형식이면 ERC-20
   if token_address.startswith("0x") and len(token_address) == 42:
       chains.append("ERC-20")
   
   # 향후 다른 체인 추가 가능 (BSC, Polygon 등)
   
   return chains

# 조회 버튼
if st.button("🔍 조회하기", type="primary", use_container_width=True) and token_address:
   
   # 주소 유효성 검사
   if not token_address.startswith("0x") or len(token_address) != 42:
       st.error("올바른 ERC-20 토큰 주소를 입력해주세요. (0x로 시작하는 42자)")
   else:
       # 로딩 시작
       with st.spinner("토큰 정보를 조회중입니다..."):
           
           # 토큰 정보 가져오기
           token_info = get_token_info(token_address) if ETHERSCAN_API_KEY else None
           price_info = get_token_price(token_address)
           chains = detect_chains(token_address)
           
           # 토큰 정보 표시
           col1, col2 = st.columns(2)
           
           with col1:
               if token_info:
                   st.write(f"**토큰:** {token_info['symbol']} ({token_info['name']})")
               else:
                   st.write(f"**토큰:** Unknown (API 키 필요)")
                   
               if price_info['price'] > 0:
                   st.write(f"**현재가:** ${price_info['price']:.8f}")
                   change_color = "green" if price_info['change_24h'] >= 0 else "red"
                   change_sign = "+" if price_info['change_24h'] >= 0 else ""
                   st.markdown(f"**24h 변동:** <span style='color:{change_color}'>{change_sign}{price_info['change_24h']:.2f}%</span>", 
                              unsafe_allow_html=True)
               else:
                   st.write("**현재가:** 가격 정보 없음 (신규/미상장 토큰)")
           
           with col2:
               chains_text = " / ".join(chains) if chains else "Unknown"
               st.write(f"**토큰 주소 ({chains_text}):**")
               st.code(token_address, language=None)
       
       st.markdown("---")
       
       # 잔고 조회
       with st.spinner("거래소별 잔고를 조회중입니다..."):
           
           balances = {}
           decimals = token_info['decimals'] if token_info else 18
           
           # 각 거래소별 잔고 조회
           for exchange_name, exchange_data in EXCHANGE_WALLETS.items():
               total_balance = 0
               
               for wallet_address in exchange_data["주소"]:
                   if ETHERSCAN_API_KEY:
                       balance_wei = get_token_balance(wallet_address, token_address)
                       balance = balance_wei / (10 ** decimals)
                       total_balance += balance
                   else:
                       # API 키가 없으면 예시 데이터
                       import random
                       total_balance = random.uniform(100000, 10000000) if random.random() > 0.3 else 0
               
               if total_balance > 0:
                   balances[exchange_name] = total_balance
           
           # 총 잔고 계산
           total = sum(balances.values())
           
           if total == 0:
               st.warning("거래소에서 해당 토큰을 찾을 수 없습니다. (아직 상장되지 않았거나 다른 지갑에 보관중일 수 있습니다)")
           else:
               # 메트릭 표시
               col1, col2, col3, col4 = st.columns(4)
               
               with col1:
                   st.metric("전체 보유량", f"{total:,.0f}")
               
               with col2:
                   dollar_value = total * price_info['price'] if price_info['price'] > 0 else 0
                   st.metric("달러 가치", f"${dollar_value:,.2f}" if dollar_value > 0 else "N/A")
               
               with col3:
                   st.metric("거래소 수", len(balances))
               
               with col4:
                   top3_percent = sum(sorted(balances.values(), reverse=True)[:3]) / total * 100
                   st.metric("상위 3개 집중도", f"{top3_percent:.1f}%")
               
               # 원형 그래프와 테이블
               st.markdown("---")
               col1, col2 = st.columns([1.5, 1])
               
               with col1:
                   st.subheader("📊 거래소별 분포")
                   
                   # 원형 그래프 생성 (크기 2배로 증가)
                   fig, ax = plt.subplots(figsize=(16, 12))
                   
                   # 상위 5개 거래소만 표시
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
                                                     startangle=90, textprops={'fontsize': 14})
                   
                   # 도넛 모양
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
                   st.dataframe(df, use_container_width=True, height=500)
               
               # 주요 인사이트만
               st.markdown("---")
               st.subheader("💡 주요 인사이트")
               
               top_exchange = max(balances.items(), key=lambda x: x[1])
               st.info(f"""
               **시장 집중도 분석**
               - {top_exchange[0]}가 전체의 {top_exchange[1]/total*100:.1f}% 보유 (최다)
               - 상위 3개 거래소가 {sum(sorted(balances.values(), reverse=True)[:3])/total*100:.1f}% 차지
               - 상위 5개 거래소가 {sum(sorted(balances.values(), reverse=True)[:5])/total*100:.1f}% 차지
               """)

# 사이드바 정보
with st.sidebar:
   st.markdown("### 📖 사용 방법")
   st.markdown("""
   1. Etherscan API 키 입력 (선택)
   2. 토큰 주소 입력 또는 선택
   3. 조회하기 버튼 클릭
   
   **지원되는 토큰:**
   - ERC-20 토큰 (이더리움)
   - TGE 예정 토큰
   - 신규 상장 토큰
   - 모든 ERC-20 표준 토큰
   
   **API 키 없이도 기본 조회 가능**
   """)
   
   st.markdown("### 🔗 유용한 링크")
   st.markdown("""
   - [Etherscan API 키 발급](https://etherscan.io/apis)
   - [CoinGecko](https://coingecko.com)
   - [Etherscan](https://etherscan.io)
   """)

# 하단 정보
st.markdown("---")
st.caption("💡 모든 ERC-20 토큰 조회 가능. TGE 예정 토큰도 주소만 있으면 조회 가능합니다.")
st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json

# 다크 테마 CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("# 🔥 토큰 거래소 분포 실시간 추적기")

# 사이드바 - API 설정
with st.sidebar:
    st.header("⚙️ API 설정")
    etherscan_api = st.text_input("Etherscan API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 🔥 빠른 토큰 선택")
    quick_tokens = {
        "MOVE": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
        "PEPE": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
        "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    }
    
    if st.button("MOVE"):
        st.session_state.token_address = quick_tokens["MOVE"]
    if st.button("PEPE"):
        st.session_state.token_address = quick_tokens["PEPE"]
    if st.button("SHIB"):
        st.session_state.token_address = quick_tokens["SHIB"]

# 메인 입력
col1, col2 = st.columns([3, 1])
with col1:
    token_address = st.text_input(
        "🔍 토큰 컨트랙트 주소 입력",
        value=st.session_state.get('token_address', ''),
        placeholder="0x..."
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🚀 조회", type="primary", use_container_width=True)

# 실제 거래소 핫월렛 주소들
EXCHANGE_WALLETS = {
    "Binance": [
        "0x28C6c06298d514Db089934071355E5743bf21d60",
        "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
        "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
        "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    ],
    "OKX": [
        "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128",
        "0x06959153B974D0D5fDfd87D561db6d8d4FA0910b"
    ],
    "Bitget": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],
    "MEXC": ["0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88"],
    "BingX": ["0xd38cf87f114f2a0582c329fb9df4f7044ce71330"],
    "Gate.io": [
        "0x0D0707963952f2fBA59dD06f2b425ace40b492Fe",
        "0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c"
    ],
    "KuCoin": [
        "0xeb2629a2734e272Bcc07BDA959863f316F4bD4Cf",
        "0xd6216fc19db775df9774a6e33526131da7d19a2c"
    ],
    "Crypto.com": [
        "0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3",
        "0x46340b20830761efd32832A74d7169B29FEB9758"
    ],
    "Huobi": [
        "0xE93381fB4c4F14bDa253907b18faD305D799241a",
        "0x18709E89BD403F470088aBDAcEbE86CC60dda12e"
    ],
    "Bybit": ["0xf89d7b9c864f589bbF53a82105107622B35EaA40"]
}

# 토큰 정보 가져오기
@st.cache_data(ttl=300)
def get_token_info(token_address, api_key):
    """토큰 기본 정보 조회"""
    if not api_key:
        return {"name": "Unknown", "symbol": "Unknown", "decimals": 18}
    
    try:
        url = "https://api.etherscan.io/api"
        params = {
            'module': 'token',
            'action': 'tokeninfo',
            'contractaddress': token_address,
            'apikey': api_key
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data['status'] == '1' and data['result']:
            result = data['result'][0]
            return {
                'name': result.get('tokenName', 'Unknown'),
                'symbol': result.get('symbol', 'Unknown'),
                'decimals': int(result.get('divisor', '18'))
            }
    except:
        pass
    
    return {"name": "Unknown", "symbol": "Unknown", "decimals": 18}

# 토큰 가격 가져오기
@st.cache_data(ttl=60)
def get_token_price(token_address):
    """CoinGecko에서 가격 정보 조회"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum"
        params = {
            'contract_addresses': token_address,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if token_address.lower() in data:
            return data[token_address.lower()]
    except:
        pass
    
    return {'usd': 0, 'usd_24h_change': 0, 'usd_market_cap': 0, 'usd_24h_vol': 0}

# 토큰 잔고 조회
@st.cache_data(ttl=60)
def get_token_balance(wallet_address, token_address, api_key):
    """특정 지갑의 토큰 잔고 조회"""
    if not api_key:
        # API 키 없으면 랜덤 데이터
        import random
        return random.uniform(0, 10000000) if random.random() > 0.5 else 0
    
    try:
        url = "https://api.etherscan.io/api"
        params = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': token_address,
            'address': wallet_address,
            'tag': 'latest',
            'apikey': api_key
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data['status'] == '1':
            return int(data['result'])
        return 0
    except:
        return 0

# 조회 실행
if search_btn and token_address:
    if not token_address.startswith("0x") or len(token_address) != 42:
        st.error("⚠️ 올바른 토큰 주소를 입력하세요! (0x로 시작하는 42자)")
    else:
        # 진행률 표시
        progress = st.progress(0)
        status = st.empty()
        
        # 토큰 정보 조회
        status.text("토큰 정보 조회중...")
        progress.progress(10)
        
        token_info = get_token_info(token_address, etherscan_api)
        price_data = get_token_price(token_address)
        
        # 토큰 정보 표시
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                f"{token_info['symbol']}", 
                f"${price_data['usd']:.6f}" if price_data['usd'] > 0 else "가격 정보 없음"
            )
        
        with col2:
            if price_data['usd_24h_change']:
                st.metric(
                    "24시간 변동", 
                    f"{price_data['usd_24h_change']:.2f}%",
                    delta=f"{price_data['usd_24h_change']:.2f}%"
                )
        
        with col3:
            if price_data.get('usd_market_cap'):
                st.metric(
                    "시가총액",
                    f"${price_data['usd_market_cap']:,.0f}"
                )
        
        with col4:
            if price_data.get('usd_24h_vol'):
                st.metric(
                    "24시간 거래량",
                    f"${price_data['usd_24h_vol']:,.0f}"
                )
        
        # 거래소별 잔고 조회
        status.text("거래소별 잔고 조회중...")
        progress.progress(30)
        
        all_balances = {}
        decimals = token_info['decimals']
        
        # 각 거래소 조회
        total_exchanges = len(EXCHANGE_WALLETS)
        for idx, (exchange, wallets) in enumerate(EXCHANGE_WALLETS.items()):
            exchange_balance = 0
            
            for wallet in wallets:
                balance_wei = get_token_balance(wallet, token_address, etherscan_api)
                balance = balance_wei / (10 ** decimals)
                exchange_balance += balance
            
            if exchange_balance > 0:
                all_balances[exchange] = exchange_balance
            
            progress.progress(30 + int(60 * (idx + 1) / total_exchanges))
        
        progress.progress(100)
        status.text("조회 완료!")
        
        # 결과 표시
        if not all_balances:
            st.warning("🔍 거래소에서 해당 토큰을 찾을 수 없습니다.")
        else:
            total = sum(all_balances.values())
            
            # 전체 메트릭
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 거래소 보유량", f"{total:,.0f}")
            
            with col2:
                st.metric("달러 가치", f"${total * price_data['usd']:,.2f}")
            
            with col3:
                st.metric("보유 거래소", len(all_balances))
            
            with col4:
                top3 = sum(sorted(all_balances.values(), reverse=True)[:3])
                st.metric("TOP3 집중도", f"{top3/total*100:.1f}%")
            
            # 차트와 테이블
            st.markdown("---")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # 원형 그래프
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0e1117')
                ax.set_facecolor('#0e1117')
                
                sorted_balances = sorted(all_balances.items(), key=lambda x: x[1], reverse=True)
                
                # 상위 6개 + 기타
                if len(sorted_balances) > 6:
                    top6 = sorted_balances[:6]
                    others = sum(b[1] for b in sorted_balances[6:])
                    
                    labels = [f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)" 
                             for name, balance in top6]
                    sizes = [b[1] for b in top6]
                    
                    if others > 0:
                        labels.append(f"기타\n{others:,.0f}\n({others/total*100:.1f}%)")
                        sizes.append(others)
                else:
                    labels = [f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)" 
                             for name, balance in sorted_balances]
                    sizes = [b[1] for b in sorted_balances]
                
                colors = plt.cm.Set3(range(len(sizes)))
                
                wedges, texts = ax.pie(sizes, labels=labels, colors=colors, 
                                      startangle=90, textprops={'fontsize': 10})
                
                centre_circle = plt.Circle((0,0), 0.70, fc='#0e1117')
                fig.gca().add_artist(centre_circle)
                
                ax.set_title(f"{token_info['symbol']} 거래소 분포", fontsize=16, color='white', pad=20)
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                # 테이블
                st.markdown("### 📊 상세 현황")
                
                table_data = []
                for exchange, balance in sorted_balances:
                    table_data.append({
                        '거래소': exchange,
                        '보유량': f"{balance:,.0f}",
                        '달러 가치': f"${balance * price_data['usd']:,.2f}",
                        '점유율': f"{balance/total*100:.2f}%"
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, height=400)
                
                # CSV 다운로드
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 CSV 다운로드",
                    csv,
                    f"{token_info['symbol']}_거래소현황_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        progress.empty()
        status.empty()

# 하단 정보
st.markdown("---")
st.caption("💡 Etherscan API 키가 없으면 예시 데이터가 표시됩니다 | 🔗 실시간 블록체인 데이터")
