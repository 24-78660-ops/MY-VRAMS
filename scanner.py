import time
import re

# Try to load OpenCV
try:
    import cv2
except Exception as e:
    raise ImportError("OpenCV (cv2) is required for scanner.py: " + str(e))

# Try to load pyzbar for scanning barcodes/QR
try:
    from pyzbar import pyzbar
    _HAS_PYZBAR = True
except Exception:
    _HAS_PYZBAR = False

def start_camera_scanner(callback, camera_index=0, window_title="Scanner - press 'q' to stop", quit_key='q'):
    """
    Opens the camera and scans for codes.
    Calls the callback function each time a code is found.
    Closes when the user presses 'q'.
    """
    # Open camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")

    # Used so the same code is not read too many times
    debounce_time = 1.0
    last_text = None
    last_time = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # If frame fails, wait a bit
                time.sleep(0.1)
                continue

            found_text = None

            # If pyzbar works, use it (supports QR + barcodes)
            if _HAS_PYZBAR:
                decoded = pyzbar.decode(frame)
                for obj in decoded:
                    try:
                        raw = obj.data.decode('utf-8', errors='ignore').strip()
                    except Exception:
                        raw = None
                    if raw:
                        found_text = raw

                    # Draw box around detected code
                    pts = obj.polygon
                    if pts:
                        pts_t = [(p.x, p.y) for p in pts]
                        for i in range(len(pts_t)):
                            cv2.line(frame, pts_t[i], pts_t[(i+1) % len(pts_t)], (0,255,0), 2)
                        try:
                            cv2.putText(frame, raw, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                        except Exception:
                            pass

                    # Stop after reading one code per frame
                    if found_text:
                        break

            else:
                # If pyzbar is not available, use basic OpenCV QR scanner
                detector = cv2.QRCodeDetector()
                raw, bbox, _ = detector.detectAndDecode(frame)
                if raw:
                    found_text = raw.strip()

                # Draw square around QR code
                if bbox is not None and len(bbox) > 0:
                    pts = bbox.astype(int).reshape(-1, 2)
                    for i in range(len(pts)):
                        cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0,255,0), 2)
                    try:
                        cv2.putText(frame, found_text or "", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                    except Exception:
                        pass

            # Only call callback if the code is new or enough time passed
            now = time.time()
            if found_text:
                if found_text != last_text or (now - last_time) > debounce_time:
                    last_text = found_text
                    last_time = now
                    try:
                        callback(found_text)
                    except Exception:
                        # Ignore callback errors so scanner keeps running
                        pass

            # Show the camera window
            cv2.imshow(window_title, frame)

            # Stop if user presses quit key
            if cv2.waitKey(1) & 0xFF == ord(quit_key):
                break

    finally:
        # Close camera and window
        cap.release()
        cv2.destroyAllWindows()
