import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from defillama import DefiLlama

def intro():
    import streamlit as st
    
    st.write("# Welcome to DEFI Terminal ")
    st.sidebar.success("Select an Analyzer above.")
    st.markdown(
        """
        DEFI Terminal is an open-source Streamlit app built specifically to analyze the crypto market. DEFI Terminal allows you to analyze thousands of protocols and pools. DEFI Terminal is powered by Defi Llama.
        
       
        DEFI Terminal consists of multiple dashboards that feature Total Value Locked vs Protocol Market Cap, and Pools APY. Select a dashboard and see what DEFI Terminal can do! 
        
        A big shoutout to the team at [Hummingbot](https://https://www.youtube.com/watch?v=l6PWbN2pDK8). Without their videos and blog posts this project would not have be been possible. Make sure you check out their excellent content!
       
        #### Want to learn more?
        - Check out the repo [Here](https://github.com/webn3ewbie/defiterm)
        - Connect with me on [LinkedIn](https://www.linkedin.com/in/joseph-biancamano/)
        - Ask a question in the Streamlit community [forums](https://discuss.streamlit.io)
        
        #### Please note this app is NOT financial advice, nor are any dashboards intended to help guide financial decisions!
    """
    )
MIN_TVL = 500000.
MIN_MCAP = 500000.
 
def get_tvl_mcap_data():
    import pandas as pd 
    # initialize api client
    llama = DefiLlama()
    # Get all protocols data
    df = pd.DataFrame(llama.get_all_protocols())
    tvl_mcap_df = df.loc[(df["tvl"]>0) & (df["mcap"]>0), ["name", "tvl", "mcap", "chain", "category", "slug"]].sort_values(by=["mcap"], ascending=False)
    return tvl_mcap_df[(tvl_mcap_df["tvl"] > MIN_TVL) & (tvl_mcap_df["mcap"]> MIN_MCAP)]

def pro_tvl():
    def get_protocols_by_chain_category(protocols: pd.DataFrame, group_by: list, nth: list):
        return protocols.sort_values('tvl', ascending=False).groupby(group_by).nth(nth).reset_index()
    st.title("Total Value Locked vs Market Cap")
    with st.spinner(text='In progress'):
        tvl_mcap_df = get_tvl_mcap_data()

        default_chains = ["Ethereum", "Solana", "Binance", "Polygon", "Avalanche"]
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
        st.subheader("All Protocols")
        st.write(tvl_mcap_df)
        
def get_treemap():
    llama = DefiLlama()
    df = pd.DataFrame(llama.get_all_protocols())
    tvl_mcap_df = df.loc[(df["tvl"]>0) & (df["mcap"]>0), ["name", "tvl", "mcap", "chain", "category", "slug"]].sort_values(by=["mcap"], ascending=False)
    default_chains = ["Ethereum", "Solana", "Binance", "Polygon", "Avalanche"]
    st.write("### Top Protocols by Category")
    chains = st.multiselect(
        "Select the chains to analyze:",
        options=tvl_mcap_df["chain"].unique(),
        default=default_chains)
    def get_protocols_by_chain_category(protocols: pd.DataFrame, group_by: list, nth: list):
        return protocols.sort_values('tvl', ascending=False).groupby(group_by).nth(nth).reset_index()
   
    groupby = st.selectbox('Group by:', [['chain', 'category'], ['category', 'chain']])
    nth = st.slider("Filter Number of Protocols Per Category", min_value=1, max_value=50)

    proto_agg = get_protocols_by_chain_category(tvl_mcap_df[tvl_mcap_df["chain"].isin(chains)], groupby, np.arange(0, nth, 1).tolist())
    groupby.append("slug")
    treemap = px.treemap(
    proto_agg, 
    path=groupby,
    values='tvl',
    height=800,
    template="plotly_dark",)
    st.plotly_chart(treemap, use_container_width=True)
    st.subheader('Protocols')
    st.write(proto_agg)

def apy_pools():
    from gsheetsdb import connect
    st.title("Defi Pools TVL & APY")
    gsheet_url = "https://docs.google.com/spreadsheets/d/1ptZhQtGKFjFsYbBYVVzsUPUqEB_cvn0YejX9BAMYnLs/edit?usp=sharing"
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    df_gsheet = pd.DataFrame(rows)
    st.write(df_gsheet)

page_names_to_funcs = {
    "Home": intro,
    "Defi TVL vs MCAP": pro_tvl,
    "Top Protocols by Category": get_treemap,
    " Pools APY": apy_pools,
}

defi_term = st.sidebar.selectbox("Choose a dashboard", page_names_to_funcs.keys())
page_names_to_funcs[defi_term]()
