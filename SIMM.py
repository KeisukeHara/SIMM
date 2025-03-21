import streamlit as st
import pandas as pd
import numpy as np
import random

def generate_crif_sample(n=100):
    portfolios = [f"PORT{str(i).zfill(3)}" for i in range(1, 6)]
    trades = [f"TRADE{str(i).zfill(3)}" for i in range(1, n+1)]
    product_classes = ["RatesFX", "Credit", "Equity", "Commodity"]
    risk_types = ["Delta", "Vega", "Curvature"]
    qualifiers = ["USD", "EUR", "JPY", "BBB", "S&P500", "Gold"]
    buckets = list(range(1, 5))
    labels = ["ATM", "OTM", "5Y", "10Y"]
    amounts = [random.randint(100000, 1000000) for _ in range(n)]
    amount_ccys = [random.choice(["USD", "EUR", "JPY", "GBP"]) for _ in range(n)]
    
    data = {
        "Portfolio ID": [random.choice(portfolios) for _ in range(n)],
        "Trade ID": trades,
        "Product Class": [random.choice(product_classes) for _ in range(n)],
        "Risk Type": [random.choice(risk_types) for _ in range(n)],
        "Qualifier": [random.choice(qualifiers) for _ in range(n)],
        "Bucket": [random.choice(buckets) for _ in range(n)],
        "Label 1": [random.choice(labels) for _ in range(n)],
        "Label 2": ["" for _ in range(n)],
        "Amount": amounts,
        "Amount CCY": amount_ccys
    }
    
    return pd.DataFrame(data)

def calculate_simm(crif_df):
    product_classes = crif_df['Product Class'].unique()
    total_im = 0
    results = []
    
    for product in product_classes:
        product_data = crif_df[crif_df['Product Class'] == product]
        risk_types = product_data['Risk Type'].unique()
        product_total = 0
        
        for risk in risk_types:
            risk_data = product_data[product_data['Risk Type'] == risk]
            buckets = risk_data['Bucket'].unique()
            risk_total = 0
            
            for bucket in buckets:
                bucket_data = risk_data[risk_data['Bucket'] == bucket]
                sensitivities = bucket_data['Amount'].values
                correlation_matrix = np.full((len(sensitivities), len(sensitivities)), 0.5)
                np.fill_diagonal(correlation_matrix, 1.0)
                bucket_im = np.sqrt(sensitivities @ correlation_matrix @ sensitivities.T)
                results.append([product, risk, bucket, bucket_im])
                risk_total += bucket_im
            
            results.append([product, risk, "Total", risk_total])
            product_total += risk_total
        
        results.append([product, "Total", "", product_total])
        total_im += product_total
    
    results.append(["Total", "", "", total_im])
    
    return pd.DataFrame(results, columns=["プロダクトクラス", "リスクタイプ", "バケット", "IM"])

st.title("ISDA SIMM 計算アプリ")

if "crif_df" not in st.session_state:
    st.session_state["crif_df"] = pd.DataFrame()

sample_generated = st.button("サンプルCRIFデータを生成")

if sample_generated:
    st.session_state["crif_df"] = generate_crif_sample()
    st.success("100件のサンプルデータを生成し、自動的に読み込みました！")

if not st.session_state["crif_df"].empty:
    st.write("### CRIFデータ（サンプルまたはアップロード）")
    st.dataframe(st.session_state["crif_df"])

uploaded_file = st.file_uploader("CRIFファイルをアップロードしてください", type=["csv"])

if uploaded_file:
    st.session_state["crif_df"] = pd.read_csv(uploaded_file)
    st.write("### CRIFデータ（アップロード後）")
    st.dataframe(st.session_state["crif_df"])

if not st.session_state["crif_df"].empty and st.button("SIMMを計算"):
    simm_results = calculate_simm(st.session_state["crif_df"])
    st.write("### SIMM 計算結果")
    st.dataframe(simm_results)
