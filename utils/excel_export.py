from datetime import datetime
from pathlib import Path
import pandas as pd


def export_to_excel(df):

    report_folder = Path(
        r"C:\Users\tomas\Desktop\Reporting\Reporty"
    )

    report_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file_name = (
        f"CRM_Report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    output_file = report_folder / file_name

    # Kopie dat
    export_df = df.copy()

    # Převod výnosů
    export_df["Odhad výnosů"] = (
        export_df["Odhad výnosů"]
        .fillna("0")
        .astype(str)
        .str.replace(" Kč", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    export_df["Odhad výnosů"] = pd.to_numeric(
        export_df["Odhad výnosů"],
        errors="coerce"
    ).fillna(0)

    # Datum uzavření
    export_df["Odhad uzavření"] = pd.to_datetime(
        export_df["Odhad uzavření"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    # Aktivní stavy
    active_states = [
        "Předáno na obchodníka",
        "Příprava nabídky",
        "Nabídka předložena",
        "Jednání o smlouvě",
        "Podepsáno - scoring",
        "Scoring"
    ]

    today = datetime.today()

    # Aktuální měsíc
    aktualni_mesic = export_df[
        (export_df["Odhad uzavření"].dt.month == today.month)
        &
        (export_df["Odhad uzavření"].dt.year == today.year)
    ]

    # Následující měsíc
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

    dalsi_mesic = export_df[
        (export_df["Odhad uzavření"].dt.month == next_month)
        &
        (export_df["Odhad uzavření"].dt.year == next_year)
    ]

    # Výhled
    vyhled = export_df[
        export_df["Odhad uzavření"] >= today
    ]

    # Volné leady
    dostupne_leady = export_df[
        (export_df["Stav příležitosti"] == "Předáno na obchodníka")
        &
        (
            export_df["Další kontakty"]
            .fillna("")
            .str.strip() == ""
        )
    ]

    # Rozpracované
    pipeline = export_df[
        export_df["Stav příležitosti"]
        .isin(active_states)
    ]

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            sheet_name="Data",
            index=False
        )

        aktualni_mesic.to_excel(
            writer,
            sheet_name="Aktualni_mesic",
            index=False
        )

        dalsi_mesic.to_excel(
            writer,
            sheet_name="Nasledujici_mesic",
            index=False
        )

        pipeline.to_excel(
            writer,
            sheet_name="Pipeline",
            index=False
        )

        vyhled.to_excel(
            writer,
            sheet_name="Vyhled",
            index=False
        )

        dostupne_leady.to_excel(
            writer,
            sheet_name="Dostupne_leady",
            index=False
        )

    return output_file