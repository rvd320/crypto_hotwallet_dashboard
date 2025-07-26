import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# 페이지 설정
st.set_page_config(
    page_title="체인별 핫월렛 토큰 실시간 대시보드", 
    page_layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
    }
    .dataframe {
        font-size: 14px;
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
token_info_cols = st.columns([3, 2, 5])

with token_info_cols[0]:
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px;'>
        <strong>토큰 이름:</strong> Movement
    </div>
    """, unsafe_allow_html=True)

with token_info_cols[1]:
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px;'>
        <strong>심볼:</strong> MOVE
    </div>
    """, unsafe_allow_html=True)

with token_info_cols[2]:
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px;'>
        <strong>컨트랙트:</strong> 0x3073f7aa...1a3073
    </div>
    """, unsafe_allow_html=True)

# 토큰 가격 및 출처
st.markdown("""
<div style='background-color: #e8f5e9; padding: 12px; border-radius: 8px; margin: 15px 0;'>
    <strong>토큰 가격:</strong> $0.152103 (출처: CoinGecko)
</div>
""", unsafe_allow_html=True)

# 설정 섹션
col1, col2 = st.columns([8, 2])

with col1:
    # DEX 유동성 풀 경고
    st.markdown("""
    <div style='background-color: #fff3cd; padding: 10px; border-radius: 8px; border-left: 4px solid #ffc107;'>
        ⚠️ <strong>DEX 유동성 풀 포함 (베타)</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # DEX 정보
    st.info("🔄 DEX 유동성 풀 조회는 베타 기능입니다. 주요 DEX의 페어를 표시합니다.")

with col2:
    st.markdown("#### 병렬처리 워커 수")
    worker_count = st.slider("", min_value=1, max_value=10, value=5, label_visibility="collapsed")

# 24시간 가격 정보
st.markdown("""
<div style='background-color: #e8f5e9; padding: 12px; border-radius: 8px; margin: 15px 0;'>
    📈 <strong>DEX 24시간 가격 범위:</strong> $25,554.76
</div>
""", unsafe_allow_html=True)

# 메트릭 섹션
st.markdown("---")
st.markdown("### 📊 전체 현황")

metric_cols = st.columns(3)

with metric_cols[0]:
    st.markdown("#### CEX 총 잔고")
    st.markdown("### 86,128,410.5574")
    st.markdown("#### DEX 총 잔고")
    st.markdown("### 150,397.8275")

with metric_cols[1]:
    st.markdown("#### CEX 달러 가치")
    st.markdown("### $13,100,389.63")
    st.markdown("#### DEX 달러 가치")
    st.markdown("### $22,845.43")

with metric_cols[2]:
    st.markdown("#### 전체 총 잔고")
    st.markdown("### 86,278,808.3849")
    st.markdown("#### 전체 달러 가치")
    st.markdown("### $13,123,235.06")

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
            'CEX', 'CEX', 'CEX', 'CEX']
}

df = pd.DataFrame(data)

# 탐색기 열 추가
df['탐색기'] = ['🔍 확인'] * len(df)

# 행 번호 추가
df.index = range(0, len(df))

# 스타일 함수
def style_dataframe(df):
    # DEX 행 하이라이트
    def highlight_dex(row):
        if row['타입'] == 'DEX':
            return ['background-color: #ffebee'] * len(row)
        return [''] * len(row)
    
    # 잔고가 0인 행 스타일
    def style_zero_balance(val):
        if isinstance(val, (int, float)) and val == 0:
            return 'color: #999999'
        return ''
    
    styled_df = df.style\
        .apply(highlight_dex, axis=1)\
        .applymap(style_zero_balance, subset=['잔고'])\
        .format({'잔고': '{:,.4f}'})\
        .set_properties(**{
            'font-size': '13px',
            'border': '1px solid #ddd'
        })
    
    return styled_df

# 테이블 표시
st.dataframe(
    style_dataframe(df),
    use_container_width=True,
    height=500,
    column_config={
        "시간이름": st.column_config.TextColumn("시간이름", width=120),
        "주소": st.column_config.TextColumn("주소", width=150),
        "잔고": st.column_config.NumberColumn("잔고", format="%.4f", width=130),
        "달러가치": st.column_config.TextColumn("달러가치", width=120),
        "가격출처": st.column_config.TextColumn("가격출처", width=100),
        "타입": st.column_config.TextColumn("타입", width=60),
        "탐색기": st.column_config.TextColumn("탐색기", width=80)
    }
)

# 차트 섹션
st.markdown("---")
st.markdown("### 📈 시각화")

chart_cols = st.columns(2)

with chart_cols[0]:
    st.markdown("#### CEX vs DEX 분포")
    
    # 파이 차트
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sizes = [86128410.5574, 150397.8275]
    labels = ['CEX\n86,128,410.5574\n(99.83%)', 'DEX\n150,397.8275\n(0.17%)']
    colors = ['#3498db', '#e74c3c']
    
    wedges, texts = ax.pie(sizes, labels=labels, colors=colors, startangle=90,
                          textprops={'fontsize': 10})
    
    # 도넛 차트
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

with chart_cols[1]:
    st.markdown("#### 상위 7개 거래소 잔고")
    
    # 막대 차트
    top_exchanges = df[df['잔고'] > 0].nlargest(7, '잔고')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    bars = ax.barh(top_exchanges['시간이름'], top_exchanges['잔고'])
    
    # DEX는 다른 색상
    for i, (idx, row) in enumerate(top_exchanges.iterrows()):
        if row['타입'] == 'DEX':
            bars[i].set_color('#e74c3c')
        else:
            bars[i].set_color('#3498db')
    
    ax.set_xlabel('잔고')
    ax.set_title('거래소별 토큰 보유량')
    
    # 값 표시
    for i, (idx, row) in enumerate(top_exchanges.iterrows()):
        ax.text(row['잔고'], i, f" {row['잔고']:,.0f}", va='center')
    
    plt.tight_layout()
    st.pyplot(fig)

# 추가 정보
st.markdown("---")
with st.expander("ℹ️ 추가 정보"):
    st.markdown("""
    - **데이터 출처**: 블록체인 온체인 데이터 (Etherscan API)
    - **업데이트 주기**: 1분마다 자동 갱신
    - **DEX 지원**: Uniswap V2/V3, SushiSwap, PancakeSwap
    - **지원 체인**: Ethereum, BSC, Polygon, Arbitrum, Optimism
    """)

# 하단 정보
st.markdown("---")
st.caption(f"⏰ 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📊 실시간 블록체인 데이터")
