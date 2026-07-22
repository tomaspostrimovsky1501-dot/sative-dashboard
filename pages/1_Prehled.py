import streamlit as st
import pandas as pd
from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Přehled")

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

    leady = df[
        (df["Stav příležitosti"] == "Předáno na obchodníka")
        &
        (df["Další kontakty"].fillna("").str.strip() != "")
    ].copy()

    leady["Obchodník"] = (
        leady["Další kontakty"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace(mapping)
    )

    leady["Odhad výnosů"] = (
        leady["Odhad výnosů"]
        .fillna("0")
        .astype(str)
        .str.replace(" Kč", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    leady["Odhad výnosů"] = pd.to_numeric(
        leady["Odhad výnosů"],
        errors="coerce"
    ).fillna(0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Počet záznamů",
            len(df)
        )

    with col2:
        st.metric(
            "Předané leady",
            len(leady)
        )

    with col3:
        st.metric(
            "Potenciál leadů",
            f"{int(leady['Odhad výnosů'].sum()):,} Kč".replace(",", " ")
        )

    st.divider()

    st.subheader("Leady podle obchodníků")

    souhrn = (
        leady.groupby("Obchodník")
        .agg(
            Počet_leadů=("Firma / osoba", "count"),
            Potenciál_Kč=("Odhad výnosů", "sum")
        )
        .reset_index()
        .sort_values("Potenciál_Kč", ascending=False)
    )

    st.dataframe(
        souhrn,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    obchodnici = sorted(
        leady["Obchodník"]
        .dropna()
        .unique()
    )

    vybrany_obchodnik = st.selectbox(
        "Vyber obchodníka",
        ["Všichni"] + obchodnici
    )

    if vybrany_obchodnik == "Všichni":
        leady_zobrazeni = leady
    else:
        leady_zobrazeni = leady[
            leady["Obchodník"] == vybrany_obchodnik
        ]

    leady_zobrazeni = leady_zobrazeni.sort_values(
        by="Odhad výnosů",
        ascending=False
    )

    st.subheader("Předáno na obchodníka")

    st.dataframe(
        leady_zobrazeni[
            [
                "Firma / osoba",
                "Obchodník",
                "Odhad výnosů",
                "Vytvořeno"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )