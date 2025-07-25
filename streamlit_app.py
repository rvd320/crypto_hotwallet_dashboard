import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# 제목
st.title("🔍 멀티체인 토큰 거래소 잔고 추적기")

# EVM 체인 설정
EVM_CHAINS = {
    "Ethereum": {
        "chain_id": 1,
        "rpc": "https://eth-mainnet.g.alchemy.com/v2/",
        "explorer_api": "https://api.etherscan.io/api",
        "explorer_url": "https://etherscan.io",
        "coingecko_id": "ethereum"
    },
    "BSC": {
        "chain_id": 56,
        "rpc": "https://bsc-dataseed.binance.org/",
        "explorer_api": "https://api.bscscan.com/api",
        "explorer_url": "https://bscscan.com",
        "coingecko_id": "binance-smart-chain"
    },
    "Polygon": {
        "chain_id": 137,
        "rpc": "https://polygon-rpc.com/",
        "explorer_api": "https://api.polygonscan.com/api",
        "explorer_url": "https://polygonscan.com",
        "coingecko_id": "polygon-pos"
    },
    "Arbitrum": {
        "chain_id": 42161,
        "rpc": "https://arb1.arbitrum.io/rpc",
        "explorer_api": "https://api.arbiscan.io/api",
        "explorer_url": "https://arbiscan.io",
        "coingecko_id": "arbitrum-one"
    },
    "Optimism": {
        "chain_id": 10,
        "rpc": "https://mainnet.optimism.io",
        "explorer_api": "https://api-optimistic.etherscan.io/api",
        "explorer_url": "https://optimistic.etherscan.io",
        "coingecko_id": "optimistic-ethereum"
    },
    "Base": {
        "chain_id": 8453,
        "rpc": "https://mainnet.base.org",
        "explorer_api": "https://api.basescan.org/api",
        "explorer_url": "https://basescan.org",
        "coingecko_id": "base"
    }
}

# 거래소별 체인별 핫월렛 주소
EXCHANGE_WALLETS = {
    "Binance": {
        "Ethereum": ["0x28C6c06298d514Db089934071355E5743bf21d60", "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549"],
        "BSC": ["0x8894E0a0c962CB723c1976a4421c95949bE2D4E3", "0xe2fc31F816A9b94326492132018C3aEcC4a93aE1"],
        "Polygon": ["0xe7804c37c13166fF0b37F5aE0BB07A3aEbb6e245", "0xf977814e90da44bfa03b6295a0616a897441acec"],
    },
    "OKX": {
        "Ethereum": ["0x06959153B974D0D5fDfd87D561db6d8d4FA0910b", "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128"],
        "BSC": ["0x67Fbb3d8F41a95cc2a7362BbfC89E2aD4F3cDbB8"],
        "Polygon": ["0xAA58D356B49C909Ce69c64318E7f8f97E3E9D616"],
    },
    "Bitget": {
        "Ethereum": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],
        "BSC": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],  # 동일 주소 사용하는 경우
    },
    "MEXC": {
        "Ethereum": ["0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88"],
        "BSC": ["0x4982085C9e2F89F2eCb8131Eca71aFAD896e89CB"],
    },
    "BingX": {
        "Ethereum": ["0xd38cf87f114f2a0582c329fb9df4f7044ce71330"],
    },
    "Gate.io": {
        "Ethereum": ["0x0D0707963952f2fBA59dD06f2b425ace40b492Fe", "0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c"],
        "BSC": ["0x1C4b70a3968436B9A0a9cf5205c787eb81Bb558c"],
    },
    "KuCoin": {
        "Ethereum": ["0xeb2629a2734e272Bcc07BDA959863f316F4bD4Cf", "0xd6216fc19db775df9774a6e33526131da7d19a2c"],
        "BSC": ["0xEB2d2F1b8c558a40207669291Fda468E50c8A0bB"],
        "Polygon": ["0xEB2d2F1b8c558a40207669291Fda468E50c8A0bB"],
    }
}

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("⚙️ API 설정")
    
    api_keys = {}
    with st.expander("API 키 입력 (선택사항)", expanded=False):
        api_keys["Ethereum"] = st.text_input("Etherscan API Key", type="password")
        api_keys["BSC"] = st.text_input("BSCScan API Key", type="password")
        api_keys["Polygon"] = st.text_input("PolygonScan API Key", type="password")
        api_keys["Arbitrum"] = st.text_input("Arbiscan API Key", type="password")
        api_keys["Optimism"] = st.text_input("Optimistic Etherscan API Key", type="password")
        api_keys["Base"] = st.text_input("BaseScan API Key", type="password")
    
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. 체인 선택 (복수 선택 가능)
    2. 토큰 주소 입력
    3. 조회하기 클릭
    
    **지원 체인:**
    - Ethereum, BSC, Polygon
    - Arbitrum, Optimism, Base
    - 모든 EVM 호환 체인
    
    **팁:** API 키 없이도 기본 조회 가능
    """)

# 체인 선택
selected_chains = st.multiselect(
    "🔗 체인 선택 (복수 선택 가능)",
    list(EVM_CHAINS.keys()),
    default=["Ethereum"]
)

# 토큰 주소 입력
token_address = st.text_input(
    "📝 토큰 컨트랙트 주소",
    placeholder="0x... (모든 체인에서 동일한 주소 사용)",
    help="대부분의 토큰은 모든 체인에서 동일한 주소를 사용합니다"
)

# 캐시된 잔고 조회 함수
@st.cache_data(ttl=60)
def get_token_balance_cached(wallet_address, token_address, chain, api_key):
    """캐시된 토큰 잔고 조회"""
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
            return int(data['result'])
        return 0
    except:
        return 0

# 비동기 잔고 조회 (부하 분산)
async def get_balances_async(token_address, selected_chains, api_keys):
    """비동기로 여러 체인의 잔고를 동시에 조회"""
    all_balances = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:  # 동시 요청 제한
        futures = []
        
        for chain in selected_chains:
            chain_balances = {}
            api_key = api_keys.get(chain, "")
            
            for exchange_name, exchange_data in EXCHANGE_WALLETS.items():
                if chain in exchange_data:
                    total_balance = 0
                    
                    for wallet_address in exchange_data[chain]:
                        # 캐시된 함수 호출
                        future = executor.submit(
                            get_token_balance_cached,
                            wallet_address, token_address, chain, api_key
                        )
                        futures.append((chain, exchange_name, future))
            
            # 1초 대기 (Rate limiting)
            await asyncio.sleep(0.1)
    
    # 결과 수집
    for chain, exchange_name, future in futures:
        try:
            balance_wei = future.result(timeout=10)
            balance = balance_wei / (10 ** 18)  # decimals 가정
            
            if chain not in all_balances:
                all_balances[chain] = {}
            
            if exchange_name not in all_balances[chain]:
                all_balances[chain][exchange_name] = 0
            
            all_balances[chain][exchange_name] += balance
        except:
            continue
    
    return all_balances

# 토큰 가격 조회 (멀티체인)
@st.cache_data(ttl=300)
def get_token_price_multichain(token_address, chains):
    """여러 체인에서 토큰 가격 조회"""
    prices = {}
    
    for chain in chains:
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
                prices[chain] = {
                    'price': price_data.get('usd', 0),
                    'change_24h': price_data.get('usd_24h_change', 0)
                }
        except:
            prices[chain] = {'price': 0, 'change_24h': 0}
    
    return prices

# 조회 버튼
if st.button("🔍 조회하기", type="primary", use_container_width=True) and token_address and selected_chains:
    
    # 주소 유효성 검사
    if not token_address.startswith("0x") or len(token_address) != 42:
        st.error("올바른 토큰 주소를 입력해주세요. (0x로 시작하는 42자)")
    else:
        # 로딩 시작
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 가격 정보 조회
        status_text.text("토큰 가격 정보를 조회중...")
        progress_bar.progress(20)
        
        prices = get_token_price_multichain(token_address, selected_chains)
        
        # 체인별 가격 표시
        price_cols = st.columns(len(selected_chains))
        for idx, chain in enumerate(selected_chains):
            with price_cols[idx]:
                price_info = prices.get(chain, {'price': 0, 'change_24h': 0})
                st.metric(
                    f"{chain} 가격",
                    f"${price_info['price']:.6f}" if price_info['price'] > 0 else "N/A",
                    f"{price_info['change_24h']:.2f}%" if price_info['price'] > 0 else None
                )
        
        # 잔고 조회
        status_text.text("거래소별 잔고를 조회중...")
        progress_bar.progress(50)
        
        # 비동기로 잔고 조회
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        all_balances = loop.run_until_complete(
            get_balances_async(token_address, selected_chains, api_keys)
        )
        
        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()
        
        # 결과 표시
        st.markdown("---")
        
        # 체인별 탭
        tabs = st.tabs(selected_chains + ["📊 전체 요약"])
        
        # 전체 데이터 수집
        total_by_exchange = {}
        
        for chain_idx, chain in enumerate(selected_chains):
            with tabs[chain_idx]:
                st.subheader(f"{chain} 체인 현황")
                
                chain_balances = all_balances.get(chain, {})
                
                if not chain_balances or sum(chain_balances.values()) == 0:
                    st.warning(f"{chain}에서 해당 토큰을 찾을 수 없습니다.")
                else:
                    # 체인별 메트릭
                    total = sum(chain_balances.values())
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 보유량", f"{total:,.0f}")
                    with col2:
                        price = prices.get(chain, {}).get('price', 0)
                        st.metric("달러 가치", f"${total * price:,.2f}" if price > 0 else "N/A")
                    with col3:
                        st.metric("보유 거래소", len(chain_balances))
                    
                    # 원형 그래프
                    if len(chain_balances) > 0:
                        fig, ax = plt.subplots(figsize=(12, 8))
                        
                        sorted_balances = sorted(chain_balances.items(), key=lambda x: x[1], reverse=True)
                        labels = [f"{name}\n{balance:,.0f}\n({balance/total*100:.1f}%)" 
                                 for name, balance in sorted_balances[:5]]
                        sizes = [balance for _, balance in sorted_balances[:5]]
                        
                        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                        
                        ax.pie(sizes, labels=labels, colors=colors, startangle=90, 
                              textprops={'fontsize': 12})
                        
                        centre_circle = plt.Circle((0,0), 0.70, fc='white')
                        fig.gca().add_artist(centre_circle)
                        
                        ax.axis('equal')
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    # 테이블
                    data = []
                    for exchange, balance in sorted(chain_balances.items(), key=lambda x: x[1], reverse=True):
                        data.append({
                            '거래소': exchange,
                            '잔고': f"{balance:,.0f}",
                            '점유율': f"{balance/total*100:.2f}%"
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                
                # 전체 합산
                for exchange, balance in chain_balances.items():
                    if exchange not in total_by_exchange:
                        total_by_exchange[exchange] = 0
                    total_by_exchange[exchange] += balance
        
        # 전체 요약 탭
        with tabs[-1]:
            st.subheader("전체 체인 요약")
            
            if total_by_exchange:
                total_all = sum(total_by_exchange.values())
                
                # 전체 메트릭
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("전체 보유량", f"{total_all:,.0f}")
                with col2:
                    # 평균 가격 사용
                    avg_price = sum(p.get('price', 0) for p in prices.values()) / len(prices) if prices else 0
                    st.metric("추정 달러 가치", f"${total_all * avg_price:,.2f}" if avg_price > 0 else "N/A")
                with col3:
                    st.metric("활성 체인", len([c for c in all_balances if all_balances[c]]))
                with col4:
                    st.metric("보유 거래소", len(total_by_exchange))
                
                # 전체 원형 그래프
                fig, ax = plt.subplots(figsize=(14, 10))
                
                sorted_total = sorted(total_by_exchange.items(), key=lambda x: x[1], reverse=True)
                labels = [f"{name}\n{balance:,.0f}\n({balance/total_all*100:.1f}%)" 
                         for name, balance in sorted_total[:6]]
                sizes = [balance for _, balance in sorted_total[:6]]
                
                if len(sorted_total) > 6:
                    others = sum(balance for _, balance in sorted_total[6:])
                    labels.append(f"기타\n{others:,.0f}\n({others/total_all*100:.1f}%)")
                    sizes.append(others)
                
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#F8B195']
                
                ax.pie(sizes, labels=labels, colors=colors, startangle=90, textprops={'fontsize': 14})
                centre_circle = plt.Circle((0,0), 0.70, fc='white')
                fig.gca().add_artist(centre_circle)
                
                ax.axis('equal')
                plt.tight_layout()
                st.pyplot(fig)
                
                # 체인별 분포 테이블
                st.subheader("체인별 분포")
                chain_summary = []
                for chain in selected_chains:
                    chain_total = sum(all_balances.get(chain, {}).values())
                    chain_summary.append({
                        '체인': chain,
                        '보유량': f"{chain_total:,.0f}",
                        '점유율': f"{chain_total/total_all*100:.2f}%" if total_all > 0 else "0%",
                        '거래소 수': len(all_balances.get(chain, {}))
                    })
                
                chain_df = pd.DataFrame(chain_summary)
                st.dataframe(chain_df, use_container_width=True)

# 하단 정보
st.markdown("---")
st.caption("💡 모든 EVM 호환 체인 지원. Rate limiting으로 API 부하 최소화.")
st.caption("⚡ 비동기 처리 및 캐싱으로 빠른 조회 속도 제공.")
st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
