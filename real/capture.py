# """Capture RealSense RGB observations with YOLO and JSON/JPEG storage."""

# import json
# import os
# import time
# import uuid
# from collections import Counter
# from pathlib import Path

# import cv2
# import numpy as np
# import pyrealsense2 as rs
# from ultralytics import YOLO


# MODEL_PATH = "yolo26n.pt"
# CONFIDENCE_THRESHOLD = 0.40
# FRAME_COUNT = 60
# WINDOW_NAME = "RealSense RGB - YOLO"

# DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# IMAGES_DIR = DATA_DIR / "images"
# METADATA_PATH = DATA_DIR / "observations.json"


# def largest_detection(model: YOLO, image: np.ndarray) -> tuple[str, float] | None:
#     """Return the class and confidence of the largest-area detected box."""
#     result = model.predict(
#         source=image,
#         conf=CONFIDENCE_THRESHOLD,
#         imgsz=640,
#         verbose=False,
#     )[0]
#     boxes = result.boxes
#     if boxes is None or len(boxes) == 0:
#         return None

#     xyxy = boxes.xyxy.cpu().numpy()
#     areas = (xyxy[:, 2] - xyxy[:, 0]) * (xyxy[:, 3] - xyxy[:, 1])
#     largest_index = int(np.argmax(areas))

#     class_id = int(boxes.cls[largest_index].item())
#     confidence = float(boxes.conf[largest_index].item())
#     return result.names[class_id], confidence


# def save_observation(class_name: str, confidence: float, image: np.ndarray) -> str:
#     """Write a JPEG and append metadata to the shared JSON dataset."""
#     IMAGES_DIR.mkdir(parents=True, exist_ok=True)
#     observation_id = uuid.uuid4().hex[:12]
#     relative_image_path = f"images/{observation_id}.jpg"
#     image_path = DATA_DIR / relative_image_path

#     if not cv2.imwrite(str(image_path), image):
#         raise RuntimeError(f"Unable to save JPEG: {image_path}")

#     if METADATA_PATH.exists():
#         observations = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
#         if not isinstance(observations, list):
#             raise ValueError("observations.json must contain a JSON array")
#     else:
#         observations = []

#     observations.append({
#         "id": observation_id,
#         "class": class_name,
#         "avg_confidence": round(confidence, 4),
#         "image": relative_image_path,
#     })

#     temporary_path = DATA_DIR / f".{observation_id}.tmp"
#     try:
#         temporary_path.write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
#         os.replace(temporary_path, METADATA_PATH)
#     finally:
#         temporary_path.unlink(missing_ok=True)

#     return observation_id


# def capture_observation(pipeline: rs.pipeline, model: YOLO) -> None:
#     """Analyze exactly FRAME_COUNT frames and store one observation."""
#     detections: list[tuple[str, float] | None] = []
#     first_image: np.ndarray | None = None
#     best_images: dict[str, tuple[float, np.ndarray]] = {}

#     print(f"Capturing {FRAME_COUNT} frames...")
#     for frame_index in range(FRAME_COUNT):
#         frames = pipeline.wait_for_frames()
#         color_frame = frames.get_color_frame()

#         if not color_frame:
#             detections.append(None)
#             continue

#         image = np.asanyarray(color_frame.get_data()).copy()
#         if first_image is None:
#             first_image = image.copy()

#         detection = largest_detection(model, image)
#         detections.append(detection)

#         if detection is not None:
#             class_name, confidence = detection
#             if class_name not in best_images or confidence > best_images[class_name][0]:
#                 best_images[class_name] = (confidence, image.copy())

#         print(f"\rProcessed {frame_index + 1}/{FRAME_COUNT}", end="", flush=True)

#     print()
#     if first_image is None:
#         print("No RGB frames received; nothing saved.")
#         return

#     counts = Counter(detection[0] for detection in detections if detection is not None)
#     if counts:
#         winning_class = counts.most_common(1)[0][0]
#         representative_image = best_images[winning_class][1]
#     else:
#         winning_class = "none"
#         representative_image = first_image

#     total_confidence = sum(
#         confidence
#         for detection in detections
#         if detection is not None
#         for class_name, confidence in [detection]
#         if class_name == winning_class
#     )
#     average_confidence = total_confidence / FRAME_COUNT

#     observation_id = save_observation(
#         class_name=winning_class,
#         confidence=average_confidence,
#         image=representative_image,
#     )
#     print(f"Saved {observation_id} | {winning_class} | {average_confidence:.1%}")


# def main() -> None:
#     model = YOLO(MODEL_PATH)

#     # Preserve the working RealSense color-only setup.
#     pipeline = rs.pipeline()
#     config = rs.config()
#     config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

#     print("Starting RealSense RGB camera...")
#     pipeline.start(config)
#     previous_time = time.perf_counter()

#     try:
#         print("Press C to capture 60 frames; Q to quit.")
#         while True:
#             frames = pipeline.wait_for_frames()
#             color_frame = frames.get_color_frame()
#             if not color_frame:
#                 continue

#             image = np.asanyarray(color_frame.get_data())
#             result = model.predict(
#                 source=image,
#                 conf=CONFIDENCE_THRESHOLD,
#                 imgsz=640,
#                 verbose=False,
#             )[0]
#             annotated = result.plot()

#             now = time.perf_counter()
#             fps = 1.0 / max(now - previous_time, 1e-6)
#             previous_time = now
#             cv2.putText(
#                 annotated,
#                 f"FPS: {fps:.1f} | C: capture | Q: quit",
#                 (10, 28),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.55,
#                 (0, 255, 0),
#                 2,
#             )
#             cv2.imshow(WINDOW_NAME, annotated)

#             key = cv2.waitKey(1) & 0xFF
#             if key == ord("c"):
#                 capture_observation(pipeline, model)
#                 previous_time = time.perf_counter()
#             elif key == ord("q"):
#                 break
#     finally:
#         pipeline.stop()
#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()


"""Capture all YOLO detections across 60 RealSense RGB frames."""

import json
import os
import time
import uuid
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO


MODEL_PATH = "yolo26n.pt"
CONFIDENCE_THRESHOLD = 0.40
FRAME_COUNT = 60
WINDOW_NAME = "RealSense RGB - YOLO"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
METADATA_PATH = DATA_DIR / "observations.json"


def extract_detections(result) -> list[dict]:
    """Extract every bounding box and confidence from a YOLO result."""
    detections = []
    boxes = result.boxes

    if boxes is None or len(boxes) == 0:
        return detections

    coordinates = boxes.xyxy.cpu().numpy()
    confidences = boxes.conf.cpu().numpy()
    class_ids = boxes.cls.cpu().numpy()

    for coordinates_xyxy, confidence, class_id in zip(
        coordinates, confidences, class_ids
    ):
        detections.append({
            "class": result.names[int(class_id)],
            "confidence": round(float(confidence), 4),
            "bbox_xyxy": [
                round(float(value), 2)
                for value in coordinates_xyxy
            ],
        })

    return detections


def summarize_classes(frames: list[dict]) -> list[dict]:
    """Summarize each class across all frames.

    Use the highest confidence for a class in each frame.
    Frames without that class contribute zero confidence.
    """
    class_confidences = defaultdict(list)
    detection_counts = defaultdict(int)

    for frame in frames:
        best_per_class = {}

        for detection in frame["detections"]:
            class_name = detection["class"]
            confidence = detection["confidence"]

            detection_counts[class_name] += 1
            best_per_class[class_name] = max(
                best_per_class.get(class_name, 0.0),
                confidence,
            )

        for class_name, confidence in best_per_class.items():
            class_confidences[class_name].append(confidence)

    summaries = []
    for class_name, confidences in class_confidences.items():
        summaries.append({
            "class": class_name,
            "avg_confidence": round(
                sum(confidences) / FRAME_COUNT, 4
            ),
            "frames_detected": len(confidences),
            "detection_count": detection_counts[class_name],
        })

    return sorted(
        summaries,
        key=lambda item: (
            item["frames_detected"],
            item["avg_confidence"],
        ),
        reverse=True,
    )


def save_observation(
    frames: list[dict],
    summaries: list[dict],
    representative_image: np.ndarray,
    representative_frame: int,
) -> str:
    """Append a capture while retaining existing observations."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    observation_id = uuid.uuid4().hex[:12]
    relative_image_path = f"images/{observation_id}.jpg"
    image_path = DATA_DIR / relative_image_path

    if not cv2.imwrite(str(image_path), representative_image):
        raise RuntimeError(f"Unable to save JPEG: {image_path}")

    if METADATA_PATH.exists():
        observations = json.loads(
            METADATA_PATH.read_text(encoding="utf-8")
        )
        if not isinstance(observations, list):
            raise ValueError(
                "observations.json must contain a JSON array"
            )
    else:
        observations = []

    dominant_class = summaries[0] if summaries else {
        "class": "none",
        "avg_confidence": 0.0,
    }

    observations.append({
        "id": observation_id,
        "class": dominant_class["class"],
        "avg_confidence": dominant_class["avg_confidence"],
        "image": relative_image_path,
        "frame_count": FRAME_COUNT,
        "representative_frame": representative_frame,
        "classes": summaries,
        "frames": frames,
    })

    temporary_path = DATA_DIR / f".{observation_id}.tmp"

    try:
        temporary_path.write_text(
            json.dumps(observations, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, METADATA_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)

    return observation_id


def capture_observation(
    pipeline: rs.pipeline,
    model: YOLO,
) -> None:
    """Analyze all detections in exactly FRAME_COUNT frames."""
    frames = []
    representative_image = None
    representative_frame = 1
    best_frame_score = (-1, -1.0)

    print(f"Capturing {FRAME_COUNT} frames...")

    for frame_index in range(1, FRAME_COUNT + 1):
        frame_set = pipeline.wait_for_frames()
        color_frame = frame_set.get_color_frame()

        if not color_frame:
            frames.append({
                "frame_index": frame_index,
                "detections": [],
            })
            continue

        image = np.asanyarray(
            color_frame.get_data()
        ).copy()

        result = model.predict(
            source=image,
            conf=CONFIDENCE_THRESHOLD,
            imgsz=640,
            verbose=False,
        )[0]

        detections = extract_detections(result)

        frames.append({
            "frame_index": frame_index,
            "detections": detections,
        })

        # Choose a representative frame with the most boxes,
        # using total confidence to break ties.
        frame_score = (
            len(detections),
            sum(item["confidence"] for item in detections),
        )

        if representative_image is None or frame_score > best_frame_score:
            representative_image = result.plot()
            representative_frame = frame_index
            best_frame_score = frame_score

        print(
            f"\rProcessed {frame_index}/{FRAME_COUNT}",
            end="",
            flush=True,
        )

    print()

    if representative_image is None:
        print("No RGB frames received; nothing saved.")
        return

    summaries = summarize_classes(frames)

    observation_id = save_observation(
        frames=frames,
        summaries=summaries,
        representative_image=representative_image,
        representative_frame=representative_frame,
    )

    print(f"Saved observation: {observation_id}")
    print(
        f"Total detections: "
        f"{sum(len(frame['detections']) for frame in frames)}"
    )

    for summary in summaries:
        print(
            f"  {summary['class']}: "
            f"{summary['avg_confidence']:.1%} avg confidence, "
            f"{summary['frames_detected']}/{FRAME_COUNT} frames, "
            f"{summary['detection_count']} boxes"
        )


def main() -> None:
    model = YOLO(MODEL_PATH)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(
        rs.stream.color,
        640,
        480,
        rs.format.bgr8,
        30,
    )

    print("Starting RealSense RGB camera...")
    pipeline.start(config)

    previous_time = time.perf_counter()

    try:
        print("Press C to capture 60 frames; Q to quit.")

        while True:
            frame_set = pipeline.wait_for_frames()
            color_frame = frame_set.get_color_frame()

            if not color_frame:
                continue

            image = np.asanyarray(color_frame.get_data())

            result = model.predict(
                source=image,
                conf=CONFIDENCE_THRESHOLD,
                imgsz=640,
                verbose=False,
            )[0]

            annotated = result.plot()

            now = time.perf_counter()
            fps = 1.0 / max(now - previous_time, 1e-6)
            previous_time = now

            cv2.putText(
                annotated,
                f"FPS: {fps:.1f} | C: capture | Q: quit",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
            )

            cv2.imshow(WINDOW_NAME, annotated)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):
                capture_observation(pipeline, model)
                previous_time = time.perf_counter()
            elif key == ord("q"):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
