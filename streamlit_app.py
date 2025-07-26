import streamlit as st
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
