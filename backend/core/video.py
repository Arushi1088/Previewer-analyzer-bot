
import cv2, os
from typing import List, Dict

def extract_keyframes(
    video_path: str,
    out_dir: str,
    min_scene_delta: float = 25.0,
    fps_cap: float = 1.0
) -> List[Dict]:
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    last_hist = None
    frames_meta = []
    frame_idx = 0
    saved_idx = 0
    ms_per_frame = 1000.0 / fps

    stride = int(max(1, fps / fps_cap)) if fps_cap else 1

    while True:
        ret, frame = cap.read()
        if not ret: break
        ts_ms = int(frame_idx * ms_per_frame)

        if frame_idx % stride != 0:
            frame_idx += 1
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv],[0,1],None,[50,60],[0,180,0,256])
        cv2.normalize(hist, hist).flatten()

        scene_change = False
        if last_hist is not None:
            diff = cv2.compareHist(last_hist, hist, cv2.HISTCMP_BHATTACHARYYA) * 100
            scene_change = diff > min_scene_delta

        if scene_change or last_hist is None:
            out_path = os.path.join(out_dir, f"frame_{saved_idx:05d}.png")
            cv2.imwrite(out_path, frame)
            frames_meta.append({"index": saved_idx, "ts_ms": ts_ms, "path": out_path})
            saved_idx += 1
            last_hist = hist

        frame_idx += 1

    cap.release()
    return frames_meta
