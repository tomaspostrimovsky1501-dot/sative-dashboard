import streamlit as st
import pandas as pd

from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Kontrola dat")

df = load_latest_csv()

if df is not None:
    render_sidebar(df)

if df is None:
    st.error("Nebyl nalezen žádný CSV soubor.")

else:

    # Odfiltrovat prohry z celé kontroly dat
    df = df[
        df["Stav příležitosti"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        != "prohra"
    ].copy()

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

    crm_names = set(
        df["Další kontakty"]
        .fillna("")
        .astype(str)
        .str.strip()
        .unique()
    )

    known_names = set(mapping.keys())

    unknown_names = sorted(
        crm_names - known_names
    )

    st.subheader("Neznámí obchodníci")

    if unknown_names:

        st.dataframe(
            pd.DataFrame(
                {"CRM jméno": unknown_names}
            ),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success(
            "Všichni obchodníci jsou namapováni."
        )

    st.divider()

    st.subheader("Chybějící obchodník")

    bez_obchodnika = df[
        df["Další kontakty"]
        .fillna("")
        .str.strip() == ""
    ]

    st.metric(
        "Počet záznamů",
        len(bez_obchodnika)
    )

    if len(bez_obchodnika) > 0:

        st.dataframe(
            bez_obchodnika[
                [
                    "Firma / osoba",
                    "Stav příležitosti"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Chybějící odhad uzavření")

    bez_uzavreni = df[
        df["Odhad uzavření"]
        .fillna("")
        .astype(str)
        .str.strip() == ""
    ]

    st.metric(
        "Počet záznamů",
        len(bez_uzavreni)
    )

    if len(bez_uzavreni) > 0:

        st.dataframe(
            bez_uzavreni[
                [
                    "Firma / osoba",
                    "Další kontakty",
                    "Stav příležitosti"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Přehled stavů")

    stavy = (
        df.groupby("Stav příležitosti")
        .size()
        .reset_index(name="Počet")
        .sort_values(
            "Počet",
            ascending=False
        )
    )

    st.dataframe(
        stavy,
        use_container_width=True,
        hide_index=True
    )