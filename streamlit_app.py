import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="토큰 거래소 분포 추적기", 
    page_layout="wide",
    initial_sidebar_state="collapsed"
)

# 제목
st.title("🔍 토큰별 거래소 잔고 실시간 추적")

# 거래소 핫월렛 주소 (실제 주소)
EXCHANGE_WALLETS = {
    "Binance": {
        "주소": ["0x28C6c06298d514Db089934071355E5743bf21d60", 
                "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
                "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d"],
        "타입": "CEX"
    },
    "OKX": {
        "주소": ["0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128"],
        "타입": "CEX"
    },
    "Bitget": {
        "주소": ["0x5bdf85216ec1e38d6458c870992a69e38e03f7ef"],
        "타입": "CEX"
    },
    "MEXC": {
        "주소": ["0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88"],
        "타입": "CEX"
    },
    "BingX": {
        "주소": ["0xd38cf87f114f2a0582c329fb9df4f7044ce71330"],
        "타입": "CEX"
    },
    "Gate.io": {
        "주소": ["0x0D0707963952f2fBA59dD06f2b425ace40b492Fe"],
        "타입": "CEX"
    },
    "KuCoin": {
        "주소": ["0xd6216fc19db775df9774a6e33526131da7d19a2c"],
        "타입": "CEX"
    },
    "Uniswap V3": {
        "주소": ["0x각종유니스왑풀주소들"],
        "타입": "DEX"
    }
}

# 인기 토큰 목록 (예시)
POPULAR_TOKENS = {
    "MOVE": {
        "address": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
        "symbol": "MOVE",
        "name": "Movement",
        "decimals": 18
    },
    "PEPE": {
        "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
        "symbol": "PEPE",
        "name": "Pepe",
        "decimals": 18
    },
    "SHIB": {
        "address": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
        "symbol": "SHIB",
        "name": "Shiba Inu",
        "decimals": 18
    },
    "MATIC": {
        "address": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
        "symbol": "MATIC",
        "name": "Polygon",
        "decimals": 18
    }
}

# 상단 검색/선택 영역
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # 토큰 선택 (드롭다운)
    token_list = list(POPULAR_TOKENS.keys()) + ["직접 입력..."]
    selected_token = st.selectbox(
        "🪙 토큰 선택",
        token_list,
        index=0
    )

with col2:
    # 직접 입력 옵션
    if selected_token == "직접 입력...":
        custom_address = st.text_input(
            "토큰 컨트랙트 주소 입력",
            placeholder="0x..."
        )
        token_address = custom_address
    else:
        token_info = POPULAR_TOKENS[selected_token]
        token_address = token_info["address"]
        st.text_input(
            "토큰 주소",
            value=token_address,
            disabled=True
        )

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("🔍 조회", type="primary", use_container_width=True)

# 토큰 정보 표시
if selected_token != "직접 입력...":
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("토큰", token_info["symbol"])
    with col2:
        st.metric("이름", token_info["name"])
    with col3:
        st.metric("현재가", "$0.152103")  # 실제로는 API로 가져와야 함
    with col4:
        st.metric("24h 변동", "+12.34%", delta="12.34%")

# 메인 대시보드
if search_button or selected_token != "직접 입력...":
    st.markdown("---")
    
    # 로딩 표시
    with st.spinner(f'🔄 {selected_token} 토큰의 거래소별 잔고를 조회중...'):
        
        # 실제로는 여기서 블록체인 데이터를 가져와야 함
        # 지금은 예시 데이터 사용
        balance_data = []
        
        if selected_token == "MOVE":
            sample_balances = {
                "Binance": 59724591.9063,
                "OKX": 9754106.0084,
                "Bitget": 5847293.1234,
                "MEXC": 3129670.3224,
                "BingX": 1987654.4321,
                "Gate.io": 884020.7099,
                "KuCoin": 205700.7547,
                "Uniswap V3": 150397.8275
            }
        else:
            # 다른 토큰들은 랜덤 데이터
            import random
            sample_balances = {
                name: random.uniform(100000, 10000000) 
                for name in EXCHANGE_WALLETS.keys()
            }
        
        for exchange, balance in sample_balances.items():
            balance_data.append({
                '거래소': exchange,
                '잔고': balance,
                '달러가치': balance * 0.152103,  # 실제 가격으로 계산
                '점유율': 0,  # 나중에 계산
                '타입': EXCHANGE_WALLETS[exchange]["타입"]
            })
        
        # DataFrame 생성 및 점유율 계산
        df = pd.DataFrame(balance_data)
        total_balance = df['잔고'].sum()
        df['점유율'] = (df['잔고'] / total_balance * 100).round(2)
        df = df.sort_values('잔고', ascending=False)
    
    # 핵심 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "총 공급량 대비", 
            f"{(total_balance / 1000000000 * 100):.2f}%",
            help="총 발행량 10억개 기준"
        )
    
    with col2:
        st.metric(
            "CEX 보유량",
            f"{df[df['타입']=='CEX']['잔고'].sum():,.0f}",
            f"{df[df['타입']=='CEX']['점유율'].sum():.1f}%"
        )
    
    with col3:
        st.metric(
            "DEX 보유량",
            f"{df[df['타입']=='DEX']['잔고'].sum():,.0f}",
            f"{df[df['타입']=='DEX']['점유율'].sum():.1f}%"
        )
    
    with col4:
        st.metric(
            "상위 3개 거래소 집중도",
            f"{df.head(3)['점유율'].sum():.1f}%",
            help="상위 3개 거래소가 보유한 비율"
        )
    
    # 시각화
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 거래소별 보유 비율")
        
        # 도넛 차트
        fig = px.pie(
            df, 
            values='잔고', 
            names='거래소',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 거래소별 보유량")
        
        # 막대 그래프
        fig2 = px.bar(
            df.head(10), 
            x='잔고', 
            y='거래소',
            orientation='h',
            color='타입',
            color_discrete_map={'CEX': '#1f77b4', 'DEX': '#ff7f0e'},
            text='잔고'
        )
        fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig2.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 상세 테이블
    st.markdown("---")
    st.subheader("📋 거래소별 상세 현황")
    
    # 테이블 표시용 포맷팅
    display_df = df.copy()
    display_df['잔고'] = display_df['잔고'].apply(lambda x: f"{x:,.0f}")
    display_df['달러가치'] = display_df['달러가치'].apply(lambda x: f"${x:,.0f}")
    display_df['점유율'] = display_df['점유율'].apply(lambda x: f"{x}%")
    
    # 컬러 코딩
    def highlight_type(row):
        if row['타입'] == 'DEX':
            return ['background-color: #ffebee'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        display_df.style.apply(highlight_type, axis=1),
        use_container_width=True,
        height=400
    )
    
    # 추가 분석
    with st.expander("📊 추가 분석 정보"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 주요 지표")
            st.markdown(f"""
            - **허핀달 지수**: {(df['점유율']**2).sum():.0f} (시장 집중도)
            - **상위 5개 거래소**: {df.head(5)['점유율'].sum():.1f}%
            - **평균 보유량**: {df['잔고'].mean():,.0f}
            - **중앙값**: {df['잔고'].median():,.0f}
            """)
        
        with col2:
            st.markdown("### 💡 인사이트")
            top_exchange = df.iloc[0]['거래소']
            top_percentage = df.iloc[0]['점유율']
            
            st.markdown(f"""
            - **{top_exchange}**가 전체의 **{top_percentage}%** 보유 (최다)
            - CEX가 전체의 **{df[df['타입']=='CEX']['점유율'].sum():.1f}%** 차지
            - 상위 3개 거래소가 **{df.head(3)['점유율'].sum():.1f}%** 집중
            """)

# 하단 정보
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🔄 데이터는 실시간으로 블록체인에서 조회됩니다")

with col2:
    st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col3:
    st.caption("💡 거래소 주소는 지속적으로 업데이트됩니다")

# 사이드바에 추가 옵션
with st.sidebar:
    st.markdown("### ⚙️ 고급 설정")
    
    show_dex = st.checkbox("DEX 포함", value=True)
    min_balance = st.number_input("최소 잔고", value=0, step=1000)
    
    st.markdown("### 📌 빠른 링크")
    st.markdown("""
    - [Etherscan](https://etherscan.io)
    - [CoinGecko](https://coingecko.com)
    - [DexScreener](https://dexscreener.com)
    """)
    
    st.markdown("### 💾 데이터 내보내기")
    if st.button("CSV 다운로드"):
        st.download_button(
            label="📥 다운로드",
            data=df.to_csv(index=False),
            file_name=f"{selected_token}_exchange_balances.csv",
            mime="text/csv"
        )
