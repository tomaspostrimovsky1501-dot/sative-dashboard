import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="SATIVE BA Dashboard",
    layout="wide"
)

if "vstup" not in st.session_state:
    st.session_state.vstup = False

DATA_FOLDER = Path("data")

csv_files = list(
    DATA_FOLDER.glob("*.csv")
)

# =====================================
# VSTUPNÍ OBRAZOVKA
# =====================================

if not st.session_state.vstup:

    st.markdown("# Výkonnostní dashboard")
    st.markdown("## SATIVE BA")

    st.write("")
    st.write("Reporting obchodních příležitostí, pipeline a forecastu")
    st.write("")

    col1, col2, col3 = st.columns([2, 3, 2])

    with col2:

        if st.button(
            "VSTOUPIT",
            use_container_width=True
        ):
            st.session_state.vstup = True
            st.rerun()

    st.stop()

# =====================================
# DASHBOARD
# =====================================

st.title("CRM Dashboard")

if csv_files:

    latest_file = max(
        csv_files,
        key=lambda f: f.stat().st_mtime
    )

    posledni_aktualizace = datetime.fromtimestamp(
        latest_file.stat().st_mtime
    )

    st.metric(
        "Poslední aktualizace dat",
        posledni_aktualizace.strftime(
            "%d.%m.%Y %H:%M"
        )
    )

else:

    st.warning(
        "Ve složce data nebyl nalezen žádný CSV soubor."
    )

st.divider()

col1, col2, col3 = st.columns([1, 3, 1])

with col2:

    if st.button(
        "🔄 AKTUALIZOVAT DATA",
        use_container_width=True
    ):
        st.rerun()

st.divider()

st.info(
    "Vyber požadovaný report v levém menu."
)