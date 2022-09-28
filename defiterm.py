import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from defillama import DefiLlama

MIN_TVL = 500000.
MIN_MCAP = 500000.

@st.cache
def get_tvl_mcap_data():
    # initialize api client
    llama = DefiLlama()
    # Get all protocols data
    df = pd.DataFrame(llama.get_all_protocols())
    tvl_mcap_df = df.loc[(df["tvl"]>0) & (df["mcap"]>0), ["name", "tvl", "mcap", "chain", "category", "slug"]].sort_values(by=["mcap"], ascending=False)
    return tvl_mcap_df[(tvl_mcap_df["tvl"] > MIN_TVL) & (tvl_mcap_df["mcap"]> MIN_MCAP)]

def get_protocols_by_chain_category(protocols: pd.DataFrame, group_by: list, nth: list):
    return protocols.sort_values('tvl', ascending=False).groupby(group_by).nth(nth).reset_index()


st.set_page_config(layout='wide')
st.title("🦉 TVL vs MCAP Analysis")
st.write("---")
with st.spinner(text='In progress'):
    tvl_mcap_df = get_tvl_mcap_data()

default_chains = ["Ethereum", "Solana", "Binance", "Polygon", "Multi-Chain", "Avalanche"]
# st.write("### Protocols filter 🦅")
# tokens = st.multiselect(
#     "Select the protocols to analyze:",
#     options=tvl_mcap_df["name"],
#     default=tvl_mcap_df[tvl_mcap_df["chain"].isin(default_chains)]["name"])

st.write("### Chains filter 🔗")
chains = st.multiselect(
    "Select the chains to analyze:",
    options=tvl_mcap_df["chain"].unique(),
    default=default_chains)

scatter = px.scatter(
    data_frame=tvl_mcap_df[tvl_mcap_df["chain"].isin(chains)],
    x="tvl",
    y="mcap",
    color="chain",
    trendline="ols",
    log_x=True,
    log_y=True,
    height=800,
    hover_data=["name"],
    template="plotly_dark",
    title="TVL vs MCAP",
    labels={
        "tvl": 'TVL (USD)',
        'mcap': 'Market Cap (USD)'
    })

st.plotly_chart(scatter, use_container_width=True)
st.write(tvl_mcap_df)

st.write("---")
st.write("### SunBurst filter 🔗")
groupby = st.selectbox('Group by:', [['chain', 'category'], ['category', 'chain']])
nth = st.slider('Top protocols by Category', min_value=1, max_value=20)

proto_agg = get_protocols_by_chain_category(tvl_mcap_df[tvl_mcap_df["chain"].isin(chains)], groupby, np.arange(0, nth, 1).tolist())
groupby.append("slug")
sunburst = px.sunburst(
    proto_agg, 
    path=groupby,
    values='tvl',
    height=800,
    title="SunBurst",
    template="plotly_dark",)

st.plotly_chart(sunburst, use_container_width=True)
st.write(proto_agg)

def eth_mcap_df():
    llama = DefiLlama()
    df = pd.DataFrame(llama.get_all_yields())
    return eth_mcap_df('uniswap')
def get_pool_yields(yields: pd.DataFrame, group_by: list, nth: list):
    return yields.sort_values('tvl', ascending=False).groupby(group_by).nth(nth).reset_index()    
st.write(get_pool_yields)
st.code("💡 Source: [DefiLlama](https://defillama.com/)")