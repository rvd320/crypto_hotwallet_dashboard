import streamlit as st
import pandas as pd
from datetime import datetime

# 제목
st.title("🔍 토큰별 거래소 잔고 추적기")

# 거래소 핫월렛 주소
EXCHANGE_WALLETS = {
    "Binance": "0x28C6c06298d514Db089934071355E5743bf21d60",
    "OKX": "0x98EC059Dc3aDFBdd63429454aEB0c990FBA4A128",
    "Bitget": "0x5bdf85216ec1e38d6458c870992a69e38e03f7ef",
    "MEXC": "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88",
    "BingX": "0xd38cf87f114f2a0582c329fb9df4f7044ce71330",
    "Gate.io": "0x0D0707963952f2fBA59dD06f2b425ace40b492Fe",
    "KuCoin": "0xd6216fc19db775df9774a6e33526131da7d19a2c",
}

# 인기 토큰
TOKENS = {
    "MOVE": "0x3073f7aaa4db83f95e9ff117424f71d4751a3073",
    "PEPE": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "SHIB": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
}

# 토큰 선택
selected_token = st.selectbox("토큰 선택", list(TOKENS.keys()))
token_address = TOKENS[selected_token]

st.write(f"**토큰 주소:** {token_address}")

if st.button("🔍 조회하기"):
    # 구분선
    st.markdown("---")
    
    # 예시 데이터
    if selected_token == "MOVE":
        balances = {
            "Binance": 59724591.91,
            "OKX": 9754106.01,
            "Bitget": 5847293.12,
            "MEXC": 3129670.32,
            "BingX": 1987654.43,
            "Gate.io": 884020.71,
            "KuCoin": 205700.75
        }
    else:
        # 다른 토큰은 임의 데이터
        import random
        balances = {k: random.uniform(100000, 10000000) for k in EXCHANGE_WALLETS.keys()}
    
    # 총 잔고 계산
    total = sum(balances.values())
    
    # 메트릭 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("전체 보유량", f"{total:,.0f}")
    
    with col2:
        st.metric("달러 가치", f"${total * 0.152:,.0f}")
    
    with col3:
        st.metric("거래소 수", len(balances))
    
    # 테이블 생성
    st.subheader("거래소별 현황")
    
    data = []
    for exchange, balance in sorted(balances.items(), key=lambda x: x[1], reverse=True):
        data.append({
            '거래소': exchange,
            '잔고': f"{balance:,.0f}",
            '점유율': f"{balance/total*100:.2f}%",
            '주소': EXCHANGE_WALLETS[exchange][:10] + "..."
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # 차트
    st.subheader("시각화")
    chart_data = pd.DataFrame({
        '거래소': list(balances.keys()),
        '잔고': list(balances.values())
    })
    st.bar_chart(chart_data.set_index('거래소'))
    
    # 인사이트
    st.subheader("주요 인사이트")
    top_exchange = max(balances.items(), key=lambda x: x[1])
    st.write(f"- **{top_exchange[0]}**가 전체의 **{top_exchange[1]/total*100:.1f}%** 보유 (최다)")
    st.write(f"- 상위 3개 거래소가 전체의 **{sum(sorted(balances.values(), reverse=True)[:3])/total*100:.1f}%** 차지")

# 정보
st.markdown("---")
st.caption("💡 실제 구현시 Web3로 블록체인에서 실시간 데이터를 가져옵니다")
