
import cv2

for index in range(10):
    camera = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)

    if camera.isOpened():
        success, frame = camera.read()

        if success:
            print(
                f"Camera {index}: "
                f"{frame.shape[1]}x{frame.shape[0]}, "
                f"{len(frame.shape)} dimensions"
            )
        else:
            print(f"Camera {index}: opened but no frame")

    camera.release()
