import streamlit as st
from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Dostupné leady")

df = load_latest_csv()

if df is not None:
    render_sidebar(df)

if df is None:
    st.error("Nebyl nalezen žádný CSV soubor.")

else:

    leady = df[
        (df["Stav příležitosti"] == "Předáno na obchodníka")
        &
        (df["Další kontakty"].fillna("").str.strip() == "")
    ]

    st.metric(
        "Počet dostupných leadů",
        len(leady)
    )

    if len(leady) > 0:

        st.dataframe(
            leady[
                [
                    "Firma / osoba",
                    "Vytvořeno",
                    "Odhad výnosů"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("Žádné volné leady nebyly nalezeny.")