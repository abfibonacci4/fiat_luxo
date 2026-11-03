"""Streamlit frontend for shared JSON + JPEG observation data."""

import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OBSERVATIONS_FILE = DATA_DIR / "observations.json"
COLUMNS = ["ID", "Class", "Avg. Confidence", "Image"]


def load_observations() -> pd.DataFrame:
    if not OBSERVATIONS_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)

    records = json.loads(OBSERVATIONS_FILE.read_text(encoding="utf-8"))
    rows = []
    for record in records:
        image_path = DATA_DIR / record["image"]
        image_data_url = None
        if image_path.is_file():
            encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
            image_data_url = f"data:image/jpeg;base64,{encoded}"

        rows.append({
            "ID": record["id"],
            "Class": record["class"],
            "Avg. Confidence": float(record["avg_confidence"]),
            "Image": image_data_url,
        })
    return pd.DataFrame(rows, columns=COLUMNS)


def main() -> None:
    st.set_page_config(page_title="Object Detection Log", layout="wide")
    st.title("Object Detection Log")
    st.caption("RealSense D435i | YOLO | 60 frames per capture")

    if st.button("Refresh"):
        st.rerun()

    observations = load_observations()
    st.metric("Total observations", len(observations))
    st.dataframe(
        observations,
        column_config={
            "ID": st.column_config.TextColumn("ID"),
            "Class": st.column_config.TextColumn("Class"),
            "Avg. Confidence": st.column_config.ProgressColumn(
                "Avg. Confidence", min_value=0.0, max_value=1.0, format="percent"
            ),
            "Image": st.column_config.ImageColumn("Image", width="medium"),
        },
        hide_index=True,
        width="stretch",
        row_height=110,
    )


if __name__ == "__main__":
    main()
