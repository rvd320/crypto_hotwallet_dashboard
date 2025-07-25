import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json
import time

# 제목
st.title("🔍 멀티체인 토큰 거래소 잔고 추적기")

# EVM 체인 설정
EVM_CHAINS = {
    "Ethereum": {
        "chain_id": 1,
        "explorer_api": "https://api.etherscan.io/api",
        "explorer_url": "https://etherscan.io",
        "coingecko_id": "ethereum"
    },
    "BSC": {
        "chain_id": 56,
        "explorer_api": "https://api.bscscan.com/api",
        "explorer_url": "https://bscscan.com",
        "coingecko_id": "binance-smart-chain"
    },
    "Polygon": {
        "chain_id": 137,
        "explorer_api": "https://api.polygonscan.com/api",
        "explorer_url": "https://polygonscan.com",
        "coingecko_id": "polygon-pos"
    },
    "Arbitrum": {
        "chain_id": 42161,
        "explorer_api": "https://api.arbiscan.io/api",
        "explorer_url": "https://arbiscan.io",
        "coingecko_id": "arbitrum-one"
    },
    "Optimism": {
        "chain_id": 10,
        "explorer_api": "https://api-optimistic.etherscan.io/api",
        "explorer_url": "https://optimistic.etherscan.io",
        "coingecko_id": "optimistic-ethereum"
    }
}

# 거래소별 체인별 핫월렛 주소
EXCHANGE_WALLETS = {
    "Binance": {
        "Ethereum": ["0x28C6c06298d514Db089934071355E5743bf21d60", "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549"],
        "BSC": ["0x8894E0a0c962CB723c1976a4421c95949bE2D4E3"],
        "Polygon": ["0xe7804c37c13166fF0b37F5aE0BB07A3aEbb6e245"],
    },
    "OKX": {
        "Ethereum": ["0x06959153B974D0D5fDfd87D561db6d8d4FA0910b"],
        "BSC": ["0x67Fbb3d8F41a95cc2a7362BbfC89E2aD4F3cDbB8"],
    },
    "Bitget": {
        "Ethereum": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],
    },
    "MEXC": {
        "Ethereum": ["0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88"],
        "BSC": ["0x4982085C9e2F89F2eCb8131Eca71aFAD896e89CB"],
    },
    "BingX": {
        "Ethereum": ["0xd38cf87f114f2a0582c329fb9df4f7044ce71330"],
    },
    "Gate.io": {
        "Ethereum": ["0x0D0707963952f2fBA59dD06f2b425ace40b492Fe"],
        "BSC": ["0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c"],
    },
    "KuCoin": {
        "Ethereum": ["0xeb2629a2734e272Bcc07BDA959863f316F4bD4Cf"],
        "BSC": ["0xEB2d2F1b8c558a40207669291Fda468E50c8A0bB"],
    }
}

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 간단한 API 키 입력
    api_key = st.text_input("Explorer API Key (선택사항)", type="password", 
                           help="Etherscan, BSCScan 등에서 발급받은 API 키")
    
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. 체인 선택
    2. 토큰 주소 입력
    3. 조회하기 클릭
    
    **지원 체인:**
    - Ethereum
    - BSC (Binance Smart Chain)
    - Polygon
    - Arbitrum
    - Optimism
    """)

# 체인 선택
selected_chains = st.multiselect(
    "🔗 체인 선택 (복수 선택 가능)",
    list(EVM_CHAINS.keys()),
    default=["Ethereum"]
)

# 토큰 주소 입력
col1, col2 = st.columns([3, 1])
with col1:
    token_address = st.text_input(
        "📝 토큰 컨트랙트 주소",
        placeholder="0x... (대부분의 토큰은 모든 체인에서 동일한 주소 사용)"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🔍 조회하기", type="primary", use_container_width=True)

# 토큰 잔고 조회 함수
@st.cache_data(ttl=60)
def get_token_balance(wallet_address, token_address, chain, api_key=""):
    """토큰 잔고 조회"""
    try:
        chain_info = EVM_CHAINS[chain]
        url = chain_info["explorer_api"]
        
        params = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': token_address,
            'address': wallet_address,
            'tag': 'latest',
            'apikey': api_key if api_key else 'YourApiKeyToken'
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data['status'] == '1':
            return int(data['result']) / (10 ** 18)  # 18 decimals 가정
        return 0
    except:
        return 0

# 토큰 가격 조회
@st.cache_data(ttl=300)
def get_token_price(token_address, chain):
    """토큰 가격 조회"""
    try:
        chain_id = EVM_CHAINS[chain]["coingecko_id"]
        url = f"https://api.coingecko.com/api/v3/simple/token_price/{chain_id}"
        params = {
            'contract_addresses': token_address,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if token_address.lower() in data:
            price_data = data[token_address.lower()]
            return {
                'price': price_data.get('usd', 0),
                'change_24h': price_data.get('usd_24h_change', 0)
            }
    except:
        pass
    
    return {'price': 0, 'change_24h': 0}

# 조회 실행
if search_btn and token_address and selected_chains:
    
    # 주소 유효성 검사
    if not token_address.startswith("0x") or len(token_address) != 42:
        st.error("올바른 토큰 주소를 입력해주세요. (0x로 시작하는 42자)")
    else:
        # 진행 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 전체 결과 저장
        all_results = {}
        
        # 체인별로 조회
        for idx, chain in enumerate(selected_chains):
            status_text.text(f"{chain} 체인 조회중...")
            progress_bar.progress((idx + 1) / len(selected_chains) * 0.8)
            
            # 가격 조회
            price_info = get_token_price(token_address, chain)
            
            # 잔고 조회
            chain_balances = {}
            
            for exchange_name, exchange_data in EXCHANGE_WALLETS.items():
                if chain in exchange_data:
                    total_balance = 0
                    
                    for wallet_address in exchange_data[chain]:
                        balance = get_token_balance(wallet_address, token_address, chain, api_key)
                        total_balance += balance
                        
                        # API 부하 방지를 위한 짧은 대기
                        time.sleep(0.1)
                    
                    if total_balance > 0:
                        chain_balances[exchange_name] = total_balance
            
            all_results[chain] = {
                'price': price_info,
                'balances': chain_balances
            }
        
        progress_bar.progress(1.0)
        status_text.text("조회 완료!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # 결과 표시
        st.markdown("---")
        
        # 가격 정보 표시
        st.subheader("💰 토큰 가격 정보")
        price_cols = st.columns(len(selected_chains))
        
        for idx, chain in enumerate(selected_chains):
            with price_cols[idx]:
                price_data = all_results[chain]['price']
                if price_data['price'] > 0:
                    st.metric(
                        f"{chain}",
                        f"${price_data['price']:.6f}",
                        f"{price_data['change_24h']:.2f}%"
                    )
                else:
                    st.metric(f"{chain}", "가격 정보 없음")
        
        st.markdown("---")
        
        # 체인별 탭으로 결과 표시
        tabs = st.tabs(selected_chains + ["📊 전체 요약"])
        
        # 전체 합계 계산용
        total_by_exchange = {}
        
        # 각 체인별 결과
        for idx, chain in enumerate(selected_chains):
            with tabs[idx]:
                st.subheader(f"🔗 {chain} 체인")
                
                balances = all_results[chain]['balances']
                price = all_results[chain]['price']['price']
                
                if not balances:
                    st.warning(f"{chain}에서 해당 토큰을 찾을 수 없습니다.")
                else:
                    # 메트릭
                    total = sum(balances.values())
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 보유량", f"{total:,.0f}")
                    with col2:
                        st.metric("달러 가치", f"${total * price:,.2f}" if price > 0 else "N/A")
                    with col3:
                        st.metric("보유 거래소", len(balances))
                    
                    # 원형 그래프
                    st.markdown("#### 거래소별 분포")
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
                    
                    # 상위 5개만 표시
                    display_balances = sorted_balances[:5]
                    others = sum(b[1] for b in sorted_balances[5:]) if len(sorted_balances) > 5 else 0
                    
                    labels = []
                    sizes = []
                    
                    for name, balance in display_balances:
                        labels.append(f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)")
                        sizes.append(balance)
                    
                    if others > 0:
                        labels.append(f"기타\n{others:,.0f}\n({others/total*100:.1f}%)")
                        sizes.append(others)
                    
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                    
                    wedges, texts = ax.pie(sizes, labels=labels, colors=colors[:len(sizes)], 
                                          startangle=90, textprops={'fontsize': 12})
                    
                    # 도넛 모양
                    centre_circle = plt.Circle((0,0), 0.70, fc='white')
                    fig.gca().add_artist(centre_circle)
                    
                    ax.axis('equal')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # 테이블
                    st.markdown("#### 상세 현황")
                    data = []
                    for exchange, balance in sorted_balances:
                        data.append({
                            '거래소': exchange,
                            '잔고': f"{balance:,.0f}",
                            '점유율': f"{balance/total*100:.2f}%",
                            '달러 가치': f"${balance * price:,.2f}" if price > 0 else "N/A"
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                
                # 전체 합산을 위한 데이터 수집
                for exchange, balance in balances.items():
                    if exchange not in total_by_exchange:
                        total_by_exchange[exchange] = 0
                    total_by_exchange[exchange] += balance
        
        # 전체 요약 탭
        with tabs[-1]:
            st.subheader("📊 전체 체인 통합 요약")
            
            if total_by_exchange:
                total_all = sum(total_by_exchange.values())
                
                # 평균 가격 계산
                prices = [all_results[chain]['price']['price'] for chain in selected_chains]
                avg_price = sum(prices) / len(prices) if prices else 0
                
                # 전체 메트릭
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("전체 보유량", f"{total_all:,.0f}")
                with col2:
                    st.metric("추정 달러 가치", f"${total_all * avg_price:,.2f}" if avg_price > 0 else "N/A")
                with col3:
                    st.metric("총 거래소 수", len(total_by_exchange))
                
                # 전체 원형 그래프
                st.markdown("#### 전체 거래소 분포")
                
                fig, ax = plt.subplots(figsize=(14, 10))
                
                sorted_total = sorted(total_by_exchange.items(), key=lambda x: x[1], reverse=True)
                
                labels = []
                sizes = []
                
                for name, balance in sorted_total[:6]:
                    labels.append(f"{name}\n{balance:,.0f}\n({balance/total_all*100:.1f}%)")
                    sizes.append(balance)
                
                if len(sorted_total) > 6:
                    others = sum(b[1] for b in sorted_total[6:])
                    labels.append(f"기타\n{others:,.0f}\n({others/total_all*100:.1f}%)")
                    sizes.append(others)
                
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#F8B195']
                
                wedges, texts = ax.pie(sizes, labels=labels, colors=colors[:len(sizes)], 
                                      startangle=90, textprops={'fontsize': 14})
                
                centre_circle = plt.Circle((0,0), 0.70, fc='white')
                fig.gca().add_artist(centre_circle)
                
                ax.axis('equal')
                plt.tight_layout()
                st.pyplot(fig)
                
                # 체인별 요약 테이블
                st.markdown("#### 체인별 분포")
                chain_data = []
                for chain in selected_chains:
                    chain_total = sum(all_results[chain]['balances'].values())
                    chain_data.append({
                        '체인': chain,
                        '보유량': f"{chain_total:,.0f}",
                        '점유율': f"{chain_total/total_all*100:.2f}%" if total_all > 0 else "0%",
                        '거래소 수': len(all_results[chain]['balances'])
                    })
                
                chain_df = pd.DataFrame(chain_data)
                st.dataframe(chain_df, use_container_width=True)
            else:
                st.warning("선택한 체인들에서 해당 토큰을 찾을 수 없습니다.")

# 하단 정보
st.markdown("---")
st.caption("💡 모든 EVM 호환 체인 지원. API 키 없이도 기본 조회 가능.")
st.caption("📌 실제 거래소 핫월렛 주소 사용. 블록체인에서 실시간 조회.")
st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
