
import time

import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO


MODEL_PATH = "yolo26n.pt"
CONFIDENCE_THRESHOLD = 0.40


def main():
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
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue

            image = np.asanyarray(color_frame.get_data())

            results = model.predict(
                source=image,
                conf=CONFIDENCE_THRESHOLD,
                imgsz=640,
                verbose=False,
            )

            annotated = results[0].plot()

            current_time = time.perf_counter()
            fps = 1.0 / max(
                current_time - previous_time,
                1e-6,
            )
            previous_time = current_time

            cv2.putText(
                annotated,
                f"FPS: {fps:.1f}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            cv2.imshow("RealSense RGB - YOLO", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
