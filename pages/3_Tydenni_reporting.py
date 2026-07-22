import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_loader import load_latest_csv
from utils.sidebar import render_sidebar

st.title("Týdenní reporting")

df = load_latest_csv()

if df is not None:
    render_sidebar(df)

if df is None:
    st.error("Nebyl nalezen žádný CSV soubor.")

else:

    # Sjednocení obchodníků
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

    # Datum vytvoření
    df["Vytvořeno"] = pd.to_datetime(
        df["Vytvořeno"],
        format="%d.%m.%Y %H:%M",
        errors="coerce"
    )

    today = datetime.today()

    start_this_week = today - timedelta(days=7)
    start_last_week = today - timedelta(days=14)

    tento_tyden = df[
        df["Vytvořeno"] >= start_this_week
    ]

    minuly_tyden = df[
        (df["Vytvořeno"] >= start_last_week)
        &
        (df["Vytvořeno"] < start_this_week)
    ]

    aktivni_stavy = [
        "Předáno na obchodníka",
        "Příprava nabídky",
        "Nabídka předložena",
        "Jednání o smlouvě",
        "Podepsáno - scoring",
        "Scoring"
    ]

    # KPI
    nove_tento = len(tento_tyden)

    vyhry_tento = len(
        tento_tyden[
            tento_tyden["Stav příležitosti"] == "Výhra"
        ]
    )

    prohry_tento = len(
        tento_tyden[
            tento_tyden["Stav příležitosti"] == "Prohra"
        ]
    )

    aktivni_tento = len(
        tento_tyden[
            tento_tyden["Stav příležitosti"].isin(
                aktivni_stavy
            )
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Nové příležitosti",
            nove_tento
        )

    with col2:
        st.metric(
            "Výhry",
            vyhry_tento
        )

    with col3:
        st.metric(
            "Prohry",
            prohry_tento
        )

    with col4:
        st.metric(
            "Aktivní",
            aktivni_tento
        )

    st.divider()

    # Porovnání týdnů

    nove_minuly = len(minuly_tyden)

    vyhry_minuly = len(
        minuly_tyden[
            minuly_tyden["Stav příležitosti"] == "Výhra"
        ]
    )

    prohry_minuly = len(
        minuly_tyden[
            minuly_tyden["Stav příležitosti"] == "Prohra"
        ]
    )

    aktivni_minuly = len(
        minuly_tyden[
            minuly_tyden["Stav příležitosti"].isin(
                aktivni_stavy
            )
        ]
    )

    st.subheader("Porovnání týdnů")

    porovnani = pd.DataFrame(
        {
            "Metrika": [
                "Nové příležitosti",
                "Výhry",
                "Prohry",
                "Aktivní"
            ],
            "Minulý týden": [
                nove_minuly,
                vyhry_minuly,
                prohry_minuly,
                aktivni_minuly
            ],
            "Tento týden": [
                nove_tento,
                vyhry_tento,
                prohry_tento,
                aktivni_tento
            ]
        }
    )

    porovnani["Rozdíl"] = (
        porovnani["Tento týden"]
        - porovnani["Minulý týden"]
    )

    st.dataframe(
        porovnani,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Výsledky obchodníků

    st.subheader("Výsledky obchodníků")

    obchodnici = []

    for obchodnik in sorted(
        tento_tyden["Obchodník"]
        .fillna("")
        .unique()
    ):

        obchodnik_df = tento_tyden[
            tento_tyden["Obchodník"] == obchodnik
        ]

        nove = len(obchodnik_df)

        vyhry = len(
            obchodnik_df[
                obchodnik_df["Stav příležitosti"] == "Výhra"
            ]
        )

        prohry = len(
            obchodnik_df[
                obchodnik_df["Stav příležitosti"] == "Prohra"
            ]
        )

        aktivni = len(
            obchodnik_df[
                obchodnik_df["Stav příležitosti"].isin(
                    aktivni_stavy
                )
            ]
        )

        obchodnici.append(
            {
                "Obchodník": obchodnik,
                "Nové": nove,
                "Výhry": vyhry,
                "Prohry": prohry,
                "Aktivní": aktivni
            }
        )

    report_obchodnici = pd.DataFrame(
        obchodnici
    ).sort_values(
        "Nové",
        ascending=False
    )

    st.dataframe(
        report_obchodnici,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Detail týdne

    st.subheader("Příležitosti vytvořené tento týden")

    st.dataframe(
        tento_tyden[
            [
                "Firma / osoba",
                "Obchodník",
                "Stav příležitosti",
                "Vytvořeno"
            ]
        ].sort_values(
            "Vytvořeno",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )