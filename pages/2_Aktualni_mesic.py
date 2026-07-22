import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Aktuální měsíc")

df = load_latest_csv()

if df is not None:
    render_sidebar(df)

if df is None:
    st.error("Nebyl nalezen žádný CSV soubor.")

else:

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

    df["Odhad uzavření"] = pd.to_datetime(
        df["Odhad uzavření"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    df["Odhad výnosů"] = (
        df["Odhad výnosů"]
        .fillna("0")
        .astype(str)
        .str.replace(" Kč", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["Odhad výnosů"] = pd.to_numeric(
        df["Odhad výnosů"],
        errors="coerce"
    ).fillna(0)

    today = datetime.today()

    current_df = df[
        (df["Odhad uzavření"].dt.month == today.month)
        &
        (df["Odhad uzavření"].dt.year == today.year)
    ].copy()

    wins = current_df[
        current_df["Stav příležitosti"] == "Výhra"
    ]

    active_states = [
        "Předáno na obchodníka",
        "Příprava nabídky",
        "Nabídka předložena",
        "Jednání o smlouvě",
        "Podepsáno - scoring",
        "Scoring"
    ]

    pipeline = current_df[
        current_df["Stav příležitosti"].isin(active_states)
    ].copy()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Výhry",
            len(wins)
        )

    with col2:
        st.metric(
            "Výhry Kč",
            f"{int(wins['Odhad výnosů'].sum()):,} Kč".replace(",", " ")
        )

    with col3:
        st.metric(
            "Rozpracované",
            len(pipeline)
        )

    with col4:
        st.metric(
            "Pipeline Kč",
            f"{int(pipeline['Odhad výnosů'].sum()):,} Kč".replace(",", " ")
        )

    st.divider()

    st.subheader("Pipeline podle obchodníků")

    graf_data = (
        pipeline.groupby("Obchodník")
        .agg(
            Pipeline_Kč=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values(
            "Pipeline_Kč",
            ascending=False
        )
    )

    fig = px.bar(
        graf_data,
        x="Obchodník",
        y="Pipeline_Kč",
        text="Pipeline_Kč"
    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("Výhry podle obchodníků")

    vyhry_po_obchodnicich = (
        wins.groupby("Obchodník")
        .agg(
            Počet_výher=("Firma / osoba", "count"),
            Hodnota=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values("Hodnota", ascending=False)
    )

    st.dataframe(
        vyhry_po_obchodnicich,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Souhrn obchodníků")

    obchodnici_summary = (
        pipeline.groupby("Obchodník")
        .agg(
            Rozpracované=("Firma / osoba", "count"),
            Pipeline_Kč=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values("Pipeline_Kč", ascending=False)
    )

    st.dataframe(
        obchodnici_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Rozpracované obchody podle stavů")

    pipeline_summary = pd.pivot_table(
        pipeline,
        index="Obchodník",
        columns="Stav příležitosti",
        values="Firma / osoba",
        aggfunc="count",
        fill_value=0
    )

    st.dataframe(
        pipeline_summary,
        use_container_width=True
    )

    st.divider()

    st.subheader("Detail rozpracovaných obchodů")

    pipeline = pipeline.sort_values(
        by="Odhad výnosů",
        ascending=False
    )

    st.dataframe(
        pipeline[
            [
                "Firma / osoba",
                "Obchodník",
                "Stav příležitosti",
                "Odhad výnosů",
                "Odhad uzavření"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )