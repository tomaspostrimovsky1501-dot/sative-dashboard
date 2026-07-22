import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Výhled")

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

    dnes = datetime.today()

    vyhled = df[
        df["Odhad uzavření"] >= dnes
    ].copy()

    vyhled["Měsíc"] = (
        vyhled["Odhad uzavření"]
        .dt.strftime("%m/%Y")
    )

    st.subheader("Výhled po měsících")

    souhrn = (
        vyhled.groupby("Měsíc")
        .agg(
            Počet_obchodů=("Firma / osoba", "count"),
            Potenciál=("Odhad výnosů", "sum")
        )
        .reset_index()
    )

    st.dataframe(
        souhrn,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Forecast po měsících")

    fig = px.bar(
        souhrn,
        x="Měsíc",
        y="Potenciál",
        text="Potenciál"
    )

    fig.update_layout(
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("Výhled podle obchodníků")

    obchodnici_vyhled = (
        vyhled.groupby("Obchodník")
        .agg(
            Počet_obchodů=("Firma / osoba", "count"),
            Potenciál=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values(
            "Potenciál",
            ascending=False
        )
    )

    st.dataframe(
        obchodnici_vyhled,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Forecast podle měsíců a obchodníků")

    forecast = (
        vyhled.groupby(
            ["Měsíc", "Obchodník"]
        )
        .agg(
            Počet_obchodů=("Firma / osoba", "count"),
            Potenciál=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values(
            ["Měsíc", "Potenciál"],
            ascending=[True, False]
        )
    )

    st.dataframe(
        forecast,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Forecast podle stavů")

    forecast_stavy = (
        vyhled.groupby(
            ["Měsíc", "Stav příležitosti"]
        )
        .agg(
            Počet_obchodů=("Firma / osoba", "count"),
            Potenciál=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values(
            ["Měsíc", "Potenciál"],
            ascending=[True, False]
        )
    )

    st.dataframe(
        forecast_stavy,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Detail forecastu")

    forecast_detail = vyhled.sort_values(
        by=["Odhad uzavření", "Odhad výnosů"],
        ascending=[True, False]
    )

    st.dataframe(
        forecast_detail[
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