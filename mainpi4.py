# 02_raspberry_pi_picamera_fall_detection_v2.py
# Run YOLOv8-Pose fall detection on Raspberry Pi 4 + Picamera2.
#
# Input:
#   PiCamera2 via CSI camera module.
#
# Keys:
#   f = set ground truth to FALL
#   n = set ground truth to NORMAL
#   u = unset ground truth
#   r = reset counters
#   q = quit
#
# Suggested easy debug:
#   python 02_raspberry_pi_picamera_fall_detection_v2.py --hold-sec 0.8 --kp-conf 0.25 --offset-px 80
#
# Final report setting suggestion:
#   python 02_raspberry_pi_picamera_fall_detection_v2.py --hold-sec 1.5 --kp-conf 0.35 --offset-px 60

import argparse
import csv
import math
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class EvalCounter:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    def reset(self):
        self.tp = self.fp = self.tn = self.fn = 0

    def update(self, pred_fall: bool, gt_label: str | None):
        if gt_label is None:
            return

        gt_fall = gt_label == "FALL"

        if pred_fall and gt_fall:
            self.tp += 1
        elif pred_fall and not gt_fall:
            self.fp += 1
        elif (not pred_fall) and (not gt_fall):
            self.tn += 1
        elif (not pred_fall) and gt_fall:
            self.fn += 1

    @property
    def accuracy(self):
        total = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / total if total else 0.0

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self):
        p = self.precision
        r = self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def parse_source(source_arg: str):
    return int(source_arg) if source_arg.isdigit() else source_arg


def get_cpu_percent() -> float:
    return float(psutil.cpu_percent(interval=None)) if psutil else -1.0


def get_ram_percent() -> float:
    return float(psutil.virtual_memory().percent) if psutil else -1.0


def get_cpu_temp_c() -> float:
    thermal_path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(thermal_path, "r", encoding="utf-8") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return -1.0


def draw_text(img, text, x, y, color=(0, 255, 0), scale=0.6, thickness=2):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


def safe_point(kp, conf, person_idx, point_idx, kp_conf_thres):
    x = float(kp[point_idx][0].item())
    y = float(kp[point_idx][1].item())

    if x == 0 or y == 0:
        return None

    if conf is not None:
        c = float(conf[person_idx][point_idx].item())
        if c < kp_conf_thres:
            return None

    return x, y


def detect_fall_by_keypoints_v2(result, keypoint_conf_thres: float, offset_px: float):
    """
    COCO/YOLOv8-Pose keypoints:
        0  = nose
        5  = left shoulder
        6  = right shoulder
        11 = left hip
        12 = right hip

    V2 heuristic uses 3 signs:
        1. Nose has dropped close to hip level.
        2. Torso angle is close to horizontal.
        3. Person bounding box is wider than tall.
    """
    debug = {
        "nose_hip": False,
        "torso_angle": None,
        "body_ar": None,
        "avg_hip_y": None,
        "nose_y": None,
        "reason": "no_person"
    }

    if result.keypoints is None or result.keypoints.xy is None or len(result.keypoints.xy) == 0:
        return False, debug

    xy = result.keypoints.xy
    conf = result.keypoints.conf
    boxes = result.boxes.xyxy if result.boxes is not None else None

    for person_idx, kp in enumerate(xy):
        if len(kp) < 13:
            continue

        nose = safe_point(kp, conf, person_idx, 0, keypoint_conf_thres)
        l_sh = safe_point(kp, conf, person_idx, 5, keypoint_conf_thres)
        r_sh = safe_point(kp, conf, person_idx, 6, keypoint_conf_thres)
        l_hip = safe_point(kp, conf, person_idx, 11, keypoint_conf_thres)
        r_hip = safe_point(kp, conf, person_idx, 12, keypoint_conf_thres)

        conditions = []

        # Condition 1: nose close to hip level
        if nose and l_hip and r_hip:
            nose_y = nose[1]
            avg_hip_y = (l_hip[1] + r_hip[1]) / 2.0
            debug["nose_y"] = round(nose_y, 1)
            debug["avg_hip_y"] = round(avg_hip_y, 1)

            nose_hip_condition = nose_y > (avg_hip_y - offset_px)
            debug["nose_hip"] = nose_hip_condition
            conditions.append(nose_hip_condition)

        # Condition 2: torso close to horizontal
        if l_sh and r_sh and l_hip and r_hip:
            shoulder_x = (l_sh[0] + r_sh[0]) / 2.0
            shoulder_y = (l_sh[1] + r_sh[1]) / 2.0
            hip_x = (l_hip[0] + r_hip[0]) / 2.0
            hip_y = (l_hip[1] + r_hip[1]) / 2.0

            dx = hip_x - shoulder_x
            dy = hip_y - shoulder_y

            # Angle from horizontal:
            # standing body is near 90 degrees, lying body is near 0 degrees.
            angle = abs(math.degrees(math.atan2(dy, dx)))
            if angle > 90:
                angle = 180 - angle

            debug["torso_angle"] = round(angle, 1)
            torso_horizontal_condition = angle < 45.0
            conditions.append(torso_horizontal_condition)

        # Condition 3: body box wider than tall
        if boxes is not None and person_idx < len(boxes):
            x1, y1, x2, y2 = [float(v.item()) for v in boxes[person_idx]]
            box_w = max(1.0, x2 - x1)
            box_h = max(1.0, y2 - y1)
            ar = box_w / box_h
            debug["body_ar"] = round(ar, 2)

            aspect_condition = ar > 1.15
            conditions.append(aspect_condition)

        # For easier detection, any strong sign can trigger temporary fall.
        # For stricter final use, replace "any(conditions)" by "sum(conditions) >= 2".
        if any(conditions):
            debug["reason"] = "fall_condition_true"
            return True, debug

    debug["reason"] = "conditions_false_or_low_conf"
    return False, debug


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="yolov8n-pose.pt")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--hold-sec", type=float, default=0.8, help="Use 0.8 for debugging; 1.5 for final report")
    parser.add_argument("--miss-tolerance-sec", type=float, default=0.4, help="Do not reset timer after one bad frame")
    parser.add_argument("--offset-px", type=float, default=80.0, help="20 is strict; 60-100 is easier for webcam testing")
    parser.add_argument("--kp-conf", type=float, default=0.25, help="0.50 is strict; 0.25-0.35 is easier for testing")
    parser.add_argument("--csv", default="raspberry_pi_picamera_metrics_v2.csv")
    args = parser.parse_args()

    print("[INFO] Loading YOLOv8-Pose model...")
    model = YOLO(args.model)

    print("[INFO] Starting Picamera2...")
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (args.width, args.height)})
    picam2.configure(config)
    picam2.start()
    time.sleep(0.5)

    fall_start_time = None
    last_temp_fall_time = None
    is_falling = False
    alarm_triggered = False
    fall_alarm_count = 0

    prev_frame_time = time.time()
    frame_id = 0
    current_gt_label = None
    eval_counter = EvalCounter()

    csv_path = Path(args.csv)
    csv_file = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    writer.writerow([
        "timestamp", "frame_id", "gt_label", "temporary_fall", "confirmed_fall",
        "fps", "ai_time_ms", "total_latency_ms", "cpu_temp_c", "cpu_percent", "ram_percent",
        "tp", "fp", "tn", "fn", "accuracy", "precision", "recall", "f1",
        "nose_y", "avg_hip_y", "torso_angle", "body_ar", "reason"
    ])

    print("[INFO] Ready.")
    print("[KEYS] f=GT FALL | n=GT NORMAL | u=unset GT | r=reset counters | q=quit")

    try:
        while True:
            loop_start = time.time()
            frame_id += 1

            frame_rgb = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            ai_start = time.time()
            results = list(model(frame_bgr, stream=True, verbose=False))
            ai_time_ms = (time.time() - ai_start) * 1000.0

            annotated_frame = frame_bgr.copy()
            temporary_fall = False
            debug_info = {}

            for r in results:
                annotated_frame = r.plot()
                fall_now, dbg = detect_fall_by_keypoints_v2(r, args.kp_conf, args.offset_px)
                debug_info = dbg
                if fall_now:
                    temporary_fall = True

            now = time.time()

            if temporary_fall:
                last_temp_fall_time = now
                if not is_falling:
                    fall_start_time = now
                    is_falling = True
                    alarm_triggered = False
            else:
                if last_temp_fall_time is None or (now - last_temp_fall_time) > args.miss_tolerance_sec:
                    is_falling = False
                    fall_start_time = None
                    alarm_triggered = False

            confirmed_fall = False
            fall_duration = 0.0

            if is_falling and fall_start_time is not None:
                fall_duration = now - fall_start_time
                if fall_duration > args.hold_sec:
                    confirmed_fall = True
                    if not alarm_triggered:
                        fall_alarm_count += 1
                        alarm_triggered = True

            if confirmed_fall:
                cv2.rectangle(annotated_frame, (10, 10), (620, 80), (0, 0, 255), cv2.FILLED)
                cv2.putText(annotated_frame, "WARNING: FALL DETECTED!", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)

            eval_counter.update(confirmed_fall, current_gt_label)

            fps = 1.0 / (now - prev_frame_time) if now > prev_frame_time else 0.0
            prev_frame_time = now
            total_latency_ms = (time.time() - loop_start) * 1000.0
            cpu_percent = get_cpu_percent()
            ram_percent = get_ram_percent()
            cpu_temp = get_cpu_temp_c()
            gt_display = current_gt_label if current_gt_label else "UNLABELED"

            draw_text(annotated_frame, f"GT: {gt_display}", 10, 115, (0, 255, 255))
            draw_text(annotated_frame, f"FPS:{fps:.2f} AI:{ai_time_ms:.1f}ms Lat:{total_latency_ms:.1f}ms", 10, 145)
            draw_text(annotated_frame, f"Temp:{cpu_temp:.1f}C CPU:{cpu_percent:.1f}% RAM:{ram_percent:.1f}%", 10, 175)
            draw_text(annotated_frame, f"TempFall:{temporary_fall} Duration:{fall_duration:.2f}s Alarms:{fall_alarm_count}", 10, 205)
            draw_text(annotated_frame, f"TP:{eval_counter.tp} FP:{eval_counter.fp} TN:{eval_counter.tn} FN:{eval_counter.fn}", 10, 235)
            draw_text(annotated_frame, f"Acc:{eval_counter.accuracy:.2f} P:{eval_counter.precision:.2f} R:{eval_counter.recall:.2f} F1:{eval_counter.f1:.2f}", 10, 265)

            nose_y = debug_info.get("nose_y")
            hip_y = debug_info.get("avg_hip_y")
            torso = debug_info.get("torso_angle")
            ar = debug_info.get("body_ar")
            reason = debug_info.get("reason", "none")

            draw_text(annotated_frame, f"NoseY:{nose_y} HipY:{hip_y}", 10, 305, (255, 255, 0))
            draw_text(annotated_frame, f"TorsoAngle:{torso} BodyAR:{ar} Reason:{reason}", 10, 335, (255, 255, 0))

            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"), frame_id, gt_display,
                int(temporary_fall), int(confirmed_fall),
                f"{fps:.4f}", f"{ai_time_ms:.4f}", f"{total_latency_ms:.4f}",
                f"{cpu_temp:.2f}", f"{cpu_percent:.2f}", f"{ram_percent:.2f}",
                eval_counter.tp, eval_counter.fp, eval_counter.tn, eval_counter.fn,
                f"{eval_counter.accuracy:.4f}", f"{eval_counter.precision:.4f}",
                f"{eval_counter.recall:.4f}", f"{eval_counter.f1:.4f}",
                nose_y, hip_y, torso, ar, reason
            ])

            cv2.imshow("YOLOv8-Pose Fall Detection V2 - Raspberry Pi", annotated_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("f"):
                current_gt_label = "FALL"
                print("[GT] FALL")
            elif key == ord("n"):
                current_gt_label = "NORMAL"
                print("[GT] NORMAL")
            elif key == ord("u"):
                current_gt_label = None
                print("[GT] UNSET")
            elif key == ord("r"):
                eval_counter.reset()
                fall_alarm_count = 0
                print("[INFO] Counters reset")

    finally:
        csv_file.close()
        picam2.stop()
        cv2.destroyAllWindows()
        print(f"[INFO] CSV saved to: {csv_path.resolve()}")
        print(f"[SUMMARY] TP={eval_counter.tp}, FP={eval_counter.fp}, TN={eval_counter.tn}, FN={eval_counter.fn}")
        print(f"[SUMMARY] Acc={eval_counter.accuracy:.4f}, P={eval_counter.precision:.4f}, R={eval_counter.recall:.4f}, F1={eval_counter.f1:.4f}")


if __name__ == "__main__":
    main()
