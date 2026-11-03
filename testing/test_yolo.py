
# import argparse
# import time

# import cv2
# from ultralytics import YOLO


# MODEL_PATH = "yolo26n.pt"
# CONFIDENCE_THRESHOLD = 0.40
# WINDOW_NAME = "Techman RealSense - YOLO"


# def open_camera(camera_index: int) -> cv2.VideoCapture:
#     camera = cv2.VideoCapture(
#         camera_index,
#         cv2.CAP_AVFOUNDATION,
#     )

#     if not camera.isOpened():
#         raise RuntimeError(
#             f"Could not open camera index {camera_index}. "
#             "Check USB connection and camera permissions."
#         )

#     camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#     camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#     return camera


# def run_detection(camera_index: int) -> None:
#     model = YOLO(MODEL_PATH)
#     camera = open_camera(camera_index)

#     previous_time = time.perf_counter()

#     try:
#         while True:
#             success, frame = camera.read()

#             if not success:
#                 print("Failed to read camera frame.")
#                 break

#             results = model.predict(
#                 source=frame,
#                 conf=CONFIDENCE_THRESHOLD,
#                 imgsz=640,
#                 verbose=False,
#             )

#             annotated_frame = results[0].plot()

#             current_time = time.perf_counter()
#             fps = 1.0 / max(
#                 current_time - previous_time, 1e-6
#             )
#             previous_time = current_time

#             cv2.putText(
#                 annotated_frame,
#                 f"FPS: {fps:.1f}",
#                 (15, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.8,
#                 (0, 255, 0),
#                 2,
#             )

#             cv2.imshow(WINDOW_NAME, annotated_frame)

#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#     finally:
#         camera.release()
#         cv2.destroyAllWindows()


# def main() -> None:
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--camera",
#         type=int,
#         default=0,
#         help="Camera index (default: 0)",
#     )

#     args = parser.parse_args()
#     run_detection(args.camera)


# if __name__ == "__main__":
#     main()


import time

import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO


ROBOT_CAMERA_WIDTH = 640
ROBOT_CAMERA_HEIGHT = 480
CAMERA_FPS = 30

MODEL_PATH = "yolo26n.pt"
CONFIDENCE_THRESHOLD = 0.40


def main() -> None:
    model = YOLO(MODEL_PATH)

    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(
        rs.stream.color,
        ROBOT_CAMERA_WIDTH,
        ROBOT_CAMERA_HEIGHT,
        rs.format.bgr8,
        CAMERA_FPS,
    )

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
                current_time - previous_time, 1e-6
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

            cv2.imshow("RealSense D435i - YOLO", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
