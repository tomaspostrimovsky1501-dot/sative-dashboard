import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_loader import load_latest_csv

st.title("Následující měsíc")

df = load_latest_csv()

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

    if dnes.month == 12:
        dalsi_mesic = 1
        dalsi_rok = dnes.year + 1
    else:
        dalsi_mesic = dnes.month + 1
        dalsi_rok = dnes.year

    aktivni_stavy = [
        "Předáno na obchodníka",
        "Příprava nabídky",
        "Nabídka předložena",
        "Jednání o smlouvě",
        "Podepsáno - scoring",
        "Scoring"
    ]

    pipeline = df[
        (df["Odhad uzavření"].dt.month == dalsi_mesic)
        &
        (df["Odhad uzavření"].dt.year == dalsi_rok)
        &
        (df["Stav příležitosti"].isin(aktivni_stavy))
    ].copy()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Počet obchodů",
            len(pipeline)
        )

    with col2:
        st.metric(
            "Hodnota pipeline",
            f"{int(pipeline['Odhad výnosů'].sum()):,} Kč".replace(",", " ")
        )

    st.divider()

    st.subheader("Pipeline podle obchodníků")

    souhrn = (
        pipeline.groupby("Obchodník")
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
        souhrn,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Rozpracované obchody podle stavů")

    st.dataframe(
        pd.pivot_table(
            pipeline,
            index="Obchodník",
            columns="Stav příležitosti",
            values="Firma / osoba",
            aggfunc="count",
            fill_value=0
        ),
        use_container_width=True
    )

    st.divider()

    st.subheader("Detail obchodů")

    st.dataframe(
        pipeline[
            [
                "Firma / osoba",
                "Obchodník",
                "Stav příležitosti",
                "Odhad výnosů",
                "Odhad uzavření"
            ]
        ].sort_values(
            "Odhad výnosů",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )