import streamlit as st
import pandas as pd
from datetime import datetime


def render_sidebar(df):

    try:

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

        df["Odhad uzavření"] = pd.to_datetime(
            df["Odhad uzavření"],
            format="%d.%m.%Y",
            errors="coerce"
        )

        dnes = datetime.today()

        aktualni_mesic = df[
            (df["Odhad uzavření"].dt.month == dnes.month)
            &
            (df["Odhad uzavření"].dt.year == dnes.year)
        ]

        vyhry = aktualni_mesic[
            aktualni_mesic["Stav příležitosti"] == "Výhra"
        ]

        leady = df[
            df["Stav příležitosti"] == "Předáno na obchodníka"
        ]

        forecast = df[
            df["Odhad uzavření"] >= dnes
        ]

        st.sidebar.markdown("---")

        st.sidebar.metric(
            "Volné leady",
            len(leady)
        )

        st.sidebar.metric(
            "Výhry měsíc",
            len(vyhry)
        )

        st.sidebar.metric(
            "Výhry Kč",
            f"{int(vyhry['Odhad výnosů'].sum()):,}".replace(",", " ")
        )

        st.sidebar.metric(
            "Forecast Kč",
            f"{int(forecast['Odhad výnosů'].sum()):,}".replace(",", " ")
        )

    except:
        pass