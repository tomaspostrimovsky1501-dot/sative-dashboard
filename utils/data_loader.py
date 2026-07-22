from pathlib import Path
import pandas as pd


def load_latest_csv():

    data_folder = Path(
        "Dashboard/Dashboard/data"
    )

    csv_files = list(
        data_folder.glob("*.csv")
    )

    if not csv_files:
        return None

    latest_file = max(
        csv_files,
        key=lambda f: f.stat().st_mtime
    )

    df = pd.read_csv(
        latest_file,
        sep=";",
        encoding="utf-8"
    )

    return df