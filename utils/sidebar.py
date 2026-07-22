import streamlit as st
import pandas as pd

from utils.excel_export import export_to_excel


def render_sidebar(df):

    sales_map = pd.read_csv(
        "obchodnici.csv",
        sep=";"
    )

    mapping = dict(
        zip(
            sales_map["crm_jmeno"],
            sales_map["dashboard_jmeno"]
        )
    )

    df["Obchodník"] = (
        df["Další kontakty"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace(mapping)
    )

    leady = df[
        df["Stav příležitosti"] == "Předáno na obchodníka"
    ]

    st.sidebar.markdown("---")

    st.sidebar.metric(
        "Volné leady",
        len(leady)
    )

    st.sidebar.metric(
        "Celkem firem",
        len(df)
    )

    st.sidebar.metric(
        "Aktivní obchodníci",
        df["Obchodník"]
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🔄 Aktualizovat data"):
        st.rerun()

    if st.sidebar.button("📊 Export do Excelu"):

        soubor = export_to_excel(df)

        st.sidebar.success(
            f"Uloženo: {soubor.name}"
        )