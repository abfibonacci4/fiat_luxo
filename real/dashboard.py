# """Streamlit frontend for shared JSON + JPEG observation data."""

# import base64
# import json
# from pathlib import Path

# import pandas as pd
# import streamlit as st

# DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# OBSERVATIONS_FILE = DATA_DIR / "observations.json"
# COLUMNS = ["ID", "Class", "Avg. Confidence", "Image"]


# def load_observations() -> pd.DataFrame:
#     if not OBSERVATIONS_FILE.exists():
#         return pd.DataFrame(columns=COLUMNS)

#     records = json.loads(OBSERVATIONS_FILE.read_text(encoding="utf-8"))
#     rows = []
#     for record in records:
#         image_path = DATA_DIR / record["image"]
#         image_data_url = None
#         if image_path.is_file():
#             encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
#             image_data_url = f"data:image/jpeg;base64,{encoded}"

#         rows.append({
#             "ID": record["id"],
#             "Class": record["class"],
#             "Avg. Confidence": float(record["avg_confidence"]),
#             "Image": image_data_url,
#         })
#     return pd.DataFrame(rows, columns=COLUMNS)


# def main() -> None:
#     st.set_page_config(page_title="Object Detection Log", layout="wide")
#     st.title("Object Detection Log")
#     st.caption("RealSense D435i | YOLO | 60 frames per capture")

#     if st.button("Refresh"):
#         st.rerun()

#     observations = load_observations()
#     st.metric("Total observations", len(observations))
#     st.dataframe(
#         observations,
#         column_config={
#             "ID": st.column_config.TextColumn("ID"),
#             "Class": st.column_config.TextColumn("Class"),
#             "Avg. Confidence": st.column_config.ProgressColumn(
#                 "Avg. Confidence", min_value=0.0, max_value=1.0, format="percent"
#             ),
#             "Image": st.column_config.ImageColumn("Image", width="medium"),
#         },
#         hide_index=True,
#         width="stretch",
#         row_height=110,
#     )


# if __name__ == "__main__":
#     main()


"""Streamlit dashboard for RealSense YOLO observations."""

import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# Assumes dashboard.py lives in the techman-dev project root.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OBSERVATIONS_FILE = DATA_DIR / "observations.json"


def load_records() -> list[dict]:
    """Load existing observations, including legacy records."""
    if not OBSERVATIONS_FILE.exists():
        return []

    records = json.loads(
        OBSERVATIONS_FILE.read_text(encoding="utf-8")
    )

    if not isinstance(records, list):
        raise ValueError("observations.json must contain a list")

    return records


def delete_record(record_id: str) -> None:
    """Delete one observation and its unshared image."""
    records = load_records()
    deleted_record = next(
        (record for record in records if record["id"] == record_id),
        None,
    )

    if deleted_record is None:
        raise ValueError(f"Capture {record_id} no longer exists.")

    remaining_records = [
        record for record in records if record["id"] != record_id
    ]
    temporary_file = OBSERVATIONS_FILE.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(remaining_records, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(OBSERVATIONS_FILE)

    image_name = deleted_record.get("image")
    image_is_shared = any(
        record.get("image") == image_name for record in remaining_records
    )

    if image_name and not image_is_shared:
        image_path = (DATA_DIR / image_name).resolve()

        try:
            image_path.relative_to(DATA_DIR.resolve())
        except ValueError:
            return

        image_path.unlink(missing_ok=True)


def image_data_url(relative_path: str) -> str | None:
    """Convert a stored JPEG into a DataFrame-compatible image URL."""
    image_path = DATA_DIR / relative_path

    if not image_path.is_file():
        return None

    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("ascii")

    return f"data:image/jpeg;base64,{encoded}"


def build_overview(records: list[dict]) -> pd.DataFrame:
    """Build a compact table containing old and new captures."""
    rows = []

    for record in records:
        summaries = record.get("classes")

        if summaries is not None:
            class_names = [
                item["class"] for item in summaries
            ]
            classes_text = ", ".join(class_names) or "none"

            total_boxes = sum(
                item["detection_count"] for item in summaries
            )
        else:
            classes_text = record.get("class", "none")
            total_boxes = None

        rows.append({
            "ID": record["id"],
            "Classes": classes_text,
            "Avg. Confidence": float(
                record.get("avg_confidence", 0.0)
            ),
            "Total Boxes": total_boxes,
            "Image": image_data_url(record["image"]),
        })

    return pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Classes",
            "Avg. Confidence",
            "Total Boxes",
            "Image",
        ],
    )


def show_capture_details(record: dict) -> None:
    """Display per-class and per-frame details for one capture."""
    summaries = record.get("classes")
    frames = record.get("frames")

    image_path = DATA_DIR / record["image"]

    if image_path.is_file():
        caption = "Representative capture image"

        if "representative_frame" in record:
            caption += (
                f" (frame {record['representative_frame']})"
            )

        st.image(str(image_path), caption=caption, width=640)

    if summaries is None or frames is None:
        st.info(
            "Legacy capture: only the original class and "
            "average confidence were stored. Individual "
            "bounding boxes are unavailable."
        )
        return

    st.subheader("Detected classes")

    if summaries:
        class_table = pd.DataFrame([
            {
                "Class": item["class"],
                "Avg. Confidence": item["avg_confidence"],
                "Frames Detected": item["frames_detected"],
                "Total Boxes": item["detection_count"],
            }
            for item in summaries
        ])

        st.dataframe(
            class_table,
            column_config={
                "Avg. Confidence": st.column_config.ProgressColumn(
                    "Avg. Confidence",
                    min_value=0.0,
                    max_value=1.0,
                    format="percent",
                ),
            },
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No objects were detected during this capture.")

    st.subheader("Frame-by-frame detections")

    frame_numbers = [
        frame["frame_index"] for frame in frames
    ]

    if not frame_numbers:
        st.info("No frame data was recorded.")
        return

    selected_frame = st.selectbox(
        "Select frame",
        options=frame_numbers,
        key=f"frame_{record['id']}",
    )

    frame = next(
        item for item in frames
        if item["frame_index"] == selected_frame
    )

    detections = frame["detections"]

    st.write(
        f"**{len(detections)} detected object(s)** "
        f"in frame {selected_frame}"
    )

    if not detections:
        st.info("No detections in this frame.")
        return

    rows = []

    for index, detection in enumerate(detections, start=1):
        x1, y1, x2, y2 = detection["bbox_xyxy"]

        rows.append({
            "Box": index,
            "Class": detection["class"],
            "Confidence": detection["confidence"],
            "X1": x1,
            "Y1": y1,
            "X2": x2,
            "Y2": y2,
        })

    st.dataframe(
        pd.DataFrame(rows),
        column_config={
            "Confidence": st.column_config.ProgressColumn(
                "Confidence",
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    if selected_frame == record.get("representative_frame"):
        st.caption(
            "The image above corresponds to this frame."
        )
    else:
        st.caption(
            "The image above shows the representative frame, "
            "not the currently selected frame. Bounding-box "
            "coordinates for the selected frame are shown "
            "in the table."
        )


def main() -> None:
    st.set_page_config(
        page_title="Object Detection Log",
        layout="wide",
    )

    st.title("Object Detection Log")
    st.caption(
        "RealSense D435i | YOLO | 60 frames per capture"
    )

    if st.button("Refresh"):
        st.rerun()

    records = list(reversed(load_records()))

    total_detections = sum(
        len(frame.get("detections", []))
        for record in records
        for frame in record.get("frames", [])
    )

    col1, col2 = st.columns(2)
    col1.metric("Total captures", len(records))
    col2.metric(
        "Recorded bounding boxes",
        total_detections,
        help="Counts boxes in new-format captures only.",
    )

    if not records:
        st.info("No observations recorded yet.")
        return

    st.subheader("Capture overview")

    overview_event = st.dataframe(
        build_overview(records),
        column_config={
            "ID": st.column_config.TextColumn("ID"),
            "Classes": st.column_config.TextColumn("Classes"),
            "Avg. Confidence": st.column_config.ProgressColumn(
                "Dominant Class Avg. Confidence",
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
            "Total Boxes": st.column_config.NumberColumn(
                "Total Boxes"
            ),
            "Image": st.column_config.ImageColumn(
                "Image",
                width="medium",
            ),
        },
        hide_index=True,
        use_container_width=True,
        row_height=110,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = overview_event.selection.rows
    selected_record_id = None

    if selected_rows:
        selected_record_id = records[selected_rows[0]]["id"]
        st.session_state.inspect_capture_id = selected_record_id

    caption_column, delete_column = st.columns([5, 1])
    caption_column.caption(
        "Select a row to spotlight it in the capture inspector."
    )

    if delete_column.button(
        "Delete selected",
        disabled=selected_record_id is None,
        use_container_width=True,
    ):
        try:
            delete_record(selected_record_id)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            st.error(f"Could not delete capture: {error}")
        else:
            if st.session_state.get("inspect_capture_id") == selected_record_id:
                del st.session_state.inspect_capture_id
            st.rerun()

    st.divider()
    st.subheader("Inspect a capture")

    capture_ids = [record["id"] for record in records]

    if st.session_state.get("inspect_capture_id") not in capture_ids:
        st.session_state.inspect_capture_id = capture_ids[0]

    selected_id = st.selectbox(
        "Select observation ID",
        options=capture_ids,
        key="inspect_capture_id",
    )

    selected_record = next(
        record for record in records
        if record["id"] == selected_id
    )

    show_capture_details(selected_record)


if __name__ == "__main__":
    main()
