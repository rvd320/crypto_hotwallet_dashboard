import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="🔥 체인별 핫월렛 대시보드", 
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("🔥 체인별 핫월렛 토큰 실시간 대시보드")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    chain = st.selectbox("체인 선택", ["ETH", "BSC", "Polygon", "Arbitrum", "Optimism"])
    st.markdown("### 병렬처리 워커 수")
    worker = st.slider("", 1, 10, 5)
    if st.button("🔄 새로고침", type="primary"):
        st.rerun()

# 토큰 정보
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**토큰 이름:** Movement")
with col2:
    st.info("**심볼:** MOVE")
with col3:
    st.info("**컨트랙트:** 0x3073f7aa...1a3073")

# 가격 정보
st.success("💰 **토큰 가격:** $0.152103 (출처: CoinGecko)")
st.warning("⚠️ DEX 유동성 풀 포함 (베타)")

# 메트릭
st.markdown("---")
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

# 테이블
st.markdown("---")
st.subheader("📊 거래소별 상세 현황")

data = {
    '거래소명': ['바낸스1', '오케엑스', '바낸스', '바낸스2', '쿠코인', 
                '바빗맷', '게이트왓', '🔥 UNISWAP (WETH 페어)'],
    '주소': ['0x28c6c062...', '0x91d40e48...', '0xdfd5293d...', '0x21a31ee1...',
            '0xe9d1e086...', '0xf89d7b9c...', '0xb80707f8...', '0xA0b413f9...'],
    '잔고': [59724591.91, 9754106.01, 7032183.93, 5387967.50,
            3129670.32, 884020.71, 205700.75, 150397.83],
    '달러가치': ['$9,084,289.60', '$1,483,628.79', '$1,069,616.27', '$819,526.03',
                '$476,032.25', '$134,462.20', '$31,287.70', '$22,845.43'],
    '타입': ['CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'CEX', 'DEX']
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True, height=400)

# 차트
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 CEX vs DEX 분포")
    chart_data = pd.DataFrame({
        'Type': ['CEX', 'DEX'],
        'Amount': [86128410.5574, 150397.8275]
    })
    st.bar_chart(chart_data.set_index('Type'))

with col2:
    st.subheader("📈 상위 5개 거래소")
    top5 = df.nlargest(5, '잔고')[['거래소명', '잔고']]
    st.bar_chart(top5.set_index('거래소명'))
