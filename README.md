# Eldercare Fall Detection with YOLOv8-Pose on Raspberry Pi 4

> Hệ thống hỗ trợ giám sát người cao tuổi bằng thị giác máy tính, chạy trực tiếp trên Raspberry Pi 4, sử dụng YOLOv8-Pose để trích xuất khung xương người và phát hiện trạng thái té ngã theo thời gian thực.

## 1. Tên dự án GitHub đề xuất

Tên repository nên dùng:

```text
eldercare-fall-detection-yolov8-pi4
```

Một số tên thay thế:

```text
yolov8-pose-fall-detection-pi4
raspberrypi4-fall-alert-yolov8-pose
edge-ai-fall-detection-picam
senior-safety-yolov8-pose
```

Tên khuyến nghị nhất là `eldercare-fall-detection-yolov8-pi4` vì ngắn gọn, dễ hiểu và thể hiện đủ 3 ý chính: người cao tuổi, phát hiện té ngã, YOLOv8 trên Raspberry Pi 4.

## 2. Giới thiệu dự án

Dự án xây dựng một hệ thống phát hiện té ngã cho người cao tuổi dựa trên thị giác máy tính. Hệ thống sử dụng Raspberry Pi 4 kết hợp module camera để thu nhận hình ảnh thời gian thực, sau đó dùng mô hình YOLOv8n-Pose để nhận diện người và trích xuất các điểm khớp cơ thể.

Khác với các thiết bị đeo như vòng tay hoặc đồng hồ thông minh, hệ thống này hoạt động theo hướng giám sát phi tiếp xúc. Người dùng không cần đeo cảm biến trên cơ thể. Toàn bộ quá trình xử lý được thực hiện trực tiếp trên Raspberry Pi 4, không cần gửi video lên máy chủ đám mây, nhờ đó tăng tính riêng tư cho người sử dụng.

Khi hệ thống phát hiện người có dấu hiệu té ngã và trạng thái này duy trì đủ lâu qua bộ lọc thời gian, chương trình sẽ hiển thị cảnh báo trực tiếp trên màn hình:

```text
WARNING: FALL DETECTED!
```

## 3. Mục tiêu chính

- Triển khai hệ thống thu nhận hình ảnh bằng Raspberry Pi 4 và module camera CSI.
- Sử dụng YOLOv8n-Pose để nhận diện người và trích xuất khung xương 17 keypoints.
- Xây dựng thuật toán Heuristics để phát hiện té ngã dựa trên vị trí mũi, vai, hông và khung bao người.
- Tích hợp bộ lọc thời gian để giảm báo động giả khi người dùng chỉ cúi xuống hoặc thay đổi tư thế tạm thời.
- Hiển thị trực quan khung xương, thông số vận hành và cảnh báo bằng OpenCV.
- Ghi dữ liệu đánh giá ra file CSV gồm FPS, thời gian suy luận, CPU, RAM, nhiệt độ và các chỉ số TP, FP, TN, FN.

## 4. Tính năng chính

- Nhận diện người bằng YOLOv8-Pose.
- Trích xuất 17 keypoints khung xương người.
- Phân tích tư thế dựa trên tọa độ mũi so với hông, góc nghiêng thân người và tỷ lệ rộng/cao của bounding box.
- Cảnh báo té ngã khi trạng thái bất thường duy trì vượt ngưỡng thời gian.
- Hiển thị video thời gian thực bằng OpenCV.
- Ghi log kết quả vào file CSV.
- Có phím gán nhãn thủ công để đánh giá mô hình.

## 5. Kiến trúc hệ thống

```text
Pi Camera / Webcam
        |
        v
Thu nhận khung hình RGB
        |
        v
Chuyển RGB sang BGR bằng OpenCV
        |
        v
YOLOv8n-Pose inference
        |
        v
Trích xuất keypoints + bounding box
        |
        v
Thuật toán Heuristics phát hiện nghi ngã
        |
        v
Bộ lọc thời gian xác nhận té ngã
        |
        v
Hiển thị cảnh báo + ghi log CSV
```

## 6. Phần cứng sử dụng

### 6.1. Raspberry Pi 4 Model B

Raspberry Pi 4 đóng vai trò là bộ xử lý trung tâm. Thiết bị chạy hệ điều hành Raspberry Pi OS, môi trường Python, OpenCV và mô hình YOLOv8n-Pose.

| Thành phần | Khuyến nghị |
|---|---|
| Board | Raspberry Pi 4 Model B |
| RAM | 4GB hoặc 8GB |
| Nguồn | USB-C 5V/3A |
| Thẻ nhớ | microSD 32GB trở lên |
| Tản nhiệt | Nên dùng quạt hoặc heatsink |
| Hiển thị | Màn hình HDMI hoặc RealVNC |

### 6.2. Camera

| Thành phần | Thông tin |
|---|---|
| Camera | Raspberry Pi Camera Module / IMX219 |
| Giao tiếp | CSI ribbon cable |
| Độ phân giải dùng trong code | 640x480 |
| Thư viện điều khiển | Picamera2 |

### 6.3. Thiết bị cảnh báo

Phiên bản hiện tại hiển thị cảnh báo trực tiếp trên màn hình bằng OpenCV. Có thể mở rộng thêm loa, buzzer, LED, email, Telegram/Zalo hoặc thông báo điện thoại.

## 7. Phần mềm và thư viện

| Thư viện | Vai trò |
|---|---|
| Python 3 | Ngôn ngữ lập trình chính |
| OpenCV | Xử lý ảnh, chuyển màu, vẽ cảnh báo, hiển thị video |
| Ultralytics | Nạp và chạy mô hình YOLOv8-Pose |
| Picamera2 | Điều khiển camera CSI trên Raspberry Pi |
| psutil | Đọc CPU, RAM |
| csv | Ghi kết quả kiểm thử ra file CSV |
| math | Tính góc thân người |
| time | Đo FPS, latency, thời gian duy trì tư thế ngã |
| pathlib | Quản lý đường dẫn file |

## 8. Cấu trúc thư mục đề xuất

```text
eldercare-fall-detection-yolov8-pi4/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── 01_windows_pc_fall_detection_v2.py
│   └── 02_raspberry_pi_picamera_fall_detection_v2.py
│
├── models/
│   └── yolov8n-pose.pt
│
├── data/
│   ├── test_videos/
│   └── sample_frames/
│
├── results/
│   ├── csv_logs/
│   └── screenshots/
│
└── docs/
    ├── report.pdf
    └── diagrams/
```

## 9. Nguyên lý thuật toán phát hiện té ngã

### 9.1. Keypoints được sử dụng

| Chỉ số keypoint | Ý nghĩa |
|---:|---|
| 0 | Mũi |
| 5 | Vai trái |
| 6 | Vai phải |
| 11 | Hông trái |
| 12 | Hông phải |

### 9.2. Điều kiện 1: Mũi gần ngang hông

Hệ thống lấy tọa độ Y của mũi và trung bình tọa độ Y của hai hông:

```text
avg_hip_y = (left_hip_y + right_hip_y) / 2
```

Điều kiện nghi ngã:

```text
nose_y > avg_hip_y - offset_px
```

Trong ảnh OpenCV, trục Y tăng từ trên xuống dưới. Khi người đứng, mũi thường nằm cao hơn hông rất nhiều. Khi người ngã hoặc nằm, mũi có xu hướng hạ xuống gần ngang hông.

### 9.3. Điều kiện 2: Thân người gần nằm ngang

Hệ thống tính trung điểm vai và trung điểm hông:

```text
shoulder_center = midpoint(left_shoulder, right_shoulder)
hip_center      = midpoint(left_hip, right_hip)
```

Sau đó tính vector từ vai đến hông:

```text
dx = hip_x - shoulder_x
dy = hip_y - shoulder_y
```

Góc thân người:

```text
angle = abs(degrees(atan2(dy, dx)))
```

Nếu góc nhỏ hơn 45 độ, thân người được xem là nghiêng mạnh hoặc gần nằm ngang:

```text
torso_horizontal_condition = angle < 45
```

### 9.4. Điều kiện 3: Bounding box rộng hơn cao

Hệ thống lấy khung bao người do YOLO trả về:

```text
x1, y1, x2, y2
```

Tính chiều rộng và chiều cao:

```text
box_w = x2 - x1
box_h = y2 - y1
BodyAR = box_w / box_h
```

Khi người đứng, khung bao thường cao hơn rộng nên `BodyAR < 1`. Khi người nằm hoặc ngã, khung bao thường rộng hơn cao nên `BodyAR > 1`.

Điều kiện nghi ngã:

```text
BodyAR > 1.15
```

### 9.5. Kết hợp điều kiện

Phiên bản hiện tại dùng logic dễ phát hiện:

```text
temporary_fall = condition_1 OR condition_2 OR condition_3
```

Nếu muốn giảm báo động giả, có thể dùng điều kiện chặt hơn:

```python
if sum(conditions) >= 2:
```

thay cho:

```python
if any(conditions):
```

### 9.6. Bộ lọc thời gian

Hệ thống không cảnh báo ngay khi chỉ có một frame nghi ngã. Khi `temporary_fall = True`, chương trình bắt đầu đếm thời gian.

Nếu trạng thái nghi ngã duy trì lâu hơn `hold-sec`, hệ thống mới xác nhận té ngã:

```text
confirmed_fall = fall_duration > hold_sec
```

Thông số khuyến nghị khi test nhanh:

```text
hold-sec = 0.8
kp-conf = 0.25
offset-px = 80
```

Thông số khuyến nghị khi báo cáo:

```text
hold-sec = 1.5
kp-conf = 0.35
offset-px = 60
```

## 10. Cài đặt trên Windows để test trước

### 10.1. Tạo môi trường ảo

```bash
python -m venv fall_env
fall_env\Scripts\activate
```

### 10.2. Cài thư viện

```bash
python -m pip install --upgrade pip
pip install ultralytics opencv-python psutil
```

### 10.3. Chạy bằng webcam

```bash
python src/01_windows_pc_fall_detection_v2.py --source 0
```

### 10.4. Chạy bằng video

```bash
python src/01_windows_pc_fall_detection_v2.py --source data/test_videos/test_fall.mp4
```

## 11. Cài đặt trên Raspberry Pi 4

### 11.1. Cập nhật hệ thống

```bash
sudo apt update
sudo apt upgrade -y
```

### 11.2. Cài gói cần thiết

```bash
sudo apt install -y python3-venv python3-pip python3-picamera2 python3-opencv
```

### 11.3. Tạo môi trường ảo

Nên dùng `--system-site-packages` để môi trường ảo có thể dùng được Picamera2 đã cài từ hệ thống:

```bash
python3 -m venv fall_env --system-site-packages
source fall_env/bin/activate
```

### 11.4. Cài thư viện Python

```bash
python -m pip install --upgrade pip
pip install ultralytics psutil
```

### 11.5. Kiểm tra camera

```bash
libcamera-hello
```

### 11.6. Chạy chương trình trên Raspberry Pi

Chạy test dễ phát hiện:

```bash
python src/02_raspberry_pi_picamera_fall_detection_v2.py --hold-sec 0.8 --kp-conf 0.25 --offset-px 80
```

Chạy với cấu hình khuyến nghị cho báo cáo:

```bash
python src/02_raspberry_pi_picamera_fall_detection_v2.py --hold-sec 1.5 --kp-conf 0.35 --offset-px 60
```

## 12. Tham số dòng lệnh

| Tham số | Mặc định | Ý nghĩa |
|---|---:|---|
| `--model` | `yolov8n-pose.pt` | File mô hình YOLOv8-Pose |
| `--width` | `640` | Chiều rộng frame |
| `--height` | `480` | Chiều cao frame |
| `--hold-sec` | `0.8` | Thời gian xác nhận ngã |
| `--miss-tolerance-sec` | `0.4` | Thời gian cho phép mất keypoint tạm thời |
| `--offset-px` | `80` | Khoảng bù khi so sánh mũi và hông |
| `--kp-conf` | `0.25` | Ngưỡng độ tin cậy keypoint |
| `--csv` | `raspberry_pi_picamera_metrics_v2.csv` | File lưu kết quả |

## 13. Phím điều khiển khi chạy chương trình

| Phím | Chức năng |
|---|---|
| `f` | Gán nhãn thật là FALL |
| `n` | Gán nhãn thật là NORMAL |
| `u` | Bỏ nhãn |
| `r` | Reset bộ đếm |
| `q` | Thoát chương trình |

Lưu ý: phím `f` không ép hệ thống báo ngã. Phím này chỉ dùng để gán nhãn thật nhằm tính TP, FP, TN, FN.

## 14. Kết quả đầu ra

### 14.1. Hiển thị trên màn hình

Giao diện OpenCV hiển thị bounding box, khung xương, FPS, AI inference time, latency, nhiệt độ CPU, CPU usage, RAM usage, TempFall, Duration, Alarms, TP, FP, TN, FN, Accuracy, Precision, Recall, F1-score, NoseY, HipY, TorsoAngle và BodyAR.

### 14.2. File CSV

Chương trình tự ghi log vào file CSV:

```text
raspberry_pi_picamera_metrics_v2.csv
```

Các cột chính:

```text
timestamp, frame_id, gt_label, temporary_fall, confirmed_fall,
fps, ai_time_ms, total_latency_ms, cpu_temp_c, cpu_percent, ram_percent,
tp, fp, tn, fn, accuracy, precision, recall, f1,
nose_y, avg_hip_y, torso_angle, body_ar, reason
```

## 15. Chỉ số đánh giá

### 15.1. Hiệu năng hệ thống

| Chỉ số | Ý nghĩa |
|---|---|
| FPS | Số khung hình xử lý mỗi giây |
| AI time | Thời gian YOLOv8-Pose xử lý một frame |
| Total latency | Tổng thời gian xử lý một vòng lặp |
| CPU temperature | Nhiệt độ Raspberry Pi |
| CPU percent | Phần trăm CPU sử dụng |
| RAM percent | Phần trăm RAM sử dụng |

### 15.2. Chất lượng nhận diện

| Chỉ số | Ý nghĩa |
|---|---|
| TP | Người thật sự ngã và hệ thống báo ngã |
| FP | Người không ngã nhưng hệ thống báo ngã |
| TN | Người không ngã và hệ thống không báo ngã |
| FN | Người ngã nhưng hệ thống không phát hiện |

Công thức:

```text
Accuracy  = (TP + TN) / (TP + FP + TN + FN)
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1-score  = 2 * Precision * Recall / (Precision + Recall)
```

## 16. Kịch bản kiểm thử đề xuất

| STT | Kịch bản | Mục tiêu |
|---:|---|---|
| 1 | Đứng bình thường | Kiểm tra hệ thống không báo nhầm |
| 2 | Đi lại trước camera | Kiểm tra ổn định keypoints |
| 3 | Ngồi xuống ghế | Kiểm tra báo động giả |
| 4 | Cúi nhặt đồ | Kiểm tra bộ lọc thời gian |
| 5 | Nằm nghỉ | Kiểm tra phân biệt nằm/ngã |
| 6 | Té ngã giả lập | Kiểm tra cảnh báo FALL DETECTED |

## 17. Kết quả thử nghiệm tham khảo

Trong thử nghiệm ban đầu trên Raspberry Pi 4 với độ phân giải 640x480, hệ thống đã hiển thị được khung người, khung xương và cảnh báo té ngã. Khi đối tượng nằm/ngã, hệ thống kích hoạt `TempFall = True`, tăng thời gian duy trì tư thế bất thường và hiển thị cảnh báo đỏ.

| Thông số | Giá trị quan sát |
|---|---:|
| FPS | Khoảng 0.7 FPS |
| AI inference time | Khoảng 1.3 giây/frame |
| CPU temperature | Khoảng 68–70°C |
| RAM usage | Khoảng 24–26% |

Kết quả này cho thấy hệ thống chạy được trên Raspberry Pi 4, nhưng cần tối ưu thêm nếu muốn triển khai thực tế với yêu cầu phản hồi nhanh hơn.

## 18. Lỗi thường gặp và cách xử lý

### 18.1. Không mở được camera

```bash
libcamera-hello
```

Kiểm tra cáp CSI, chiều cắm cáp và bật camera trong Raspberry Pi OS.

### 18.2. Lỗi không import được Picamera2

```bash
sudo apt install -y python3-picamera2
python3 -m venv fall_env --system-site-packages
```

### 18.3. FPS quá thấp

Có thể thử giảm độ phân giải xuống 320x240, tăng `kp-conf`, chuyển mô hình sang NCNN/ONNX, dùng Raspberry Pi 5 hoặc thêm cơ chế frame skipping.

### 18.4. Báo nhầm khi cúi người

Có thể tăng thời gian xác nhận:

```bash
--hold-sec 1.5
```

Hoặc sửa logic:

```python
if sum(conditions) >= 2:
```

### 18.5. Không hiện cửa sổ OpenCV khi SSH

Nếu chạy qua SSH không có giao diện đồ họa, hãy dùng RealVNC hoặc kết nối màn hình HDMI.

## 19. Đưa dự án lên GitHub

### 19.1. Khởi tạo repository

```bash
git init
git add .
git commit -m "Initial commit: YOLOv8-Pose fall detection on Raspberry Pi 4"
```

### 19.2. Tạo repository trên GitHub

Tên repository khuyến nghị:

```text
eldercare-fall-detection-yolov8-pi4
```

### 19.3. Kết nối remote và push

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/eldercare-fall-detection-yolov8-pi4.git
git push -u origin main
```

## 20. Hướng phát triển tiếp theo

- Chuyển mô hình sang NCNN, TensorFlow Lite hoặc ONNX để tăng tốc.
- Tích hợp Coral USB Accelerator, Hailo AI Kit hoặc Raspberry Pi 5.
- Bổ sung gửi cảnh báo qua Telegram, Zalo, email hoặc điện thoại.
- Lưu nhật ký sự kiện thay vì lưu toàn bộ video để bảo vệ quyền riêng tư.
- Xây dựng dashboard theo dõi FPS, nhiệt độ, số lần cảnh báo và trạng thái hệ thống.
- Thu thập thêm dữ liệu thực nghiệm để đánh giá Accuracy, Precision, Recall và F1-score khách quan hơn.
- Theo dõi ID người qua nhiều frame để giảm báo động giả.
- Phân tích vận tốc hông, vai và đầu theo chuỗi thời gian.

## 21. Ghi chú về quyền riêng tư

Dự án hướng đến xử lý tại biên. Video không cần gửi lên cloud. Khi mở rộng hệ thống, nên ưu tiên chỉ lưu sự kiện cảnh báo hoặc ảnh minh chứng khi thật sự cần thiết, tránh lưu toàn bộ video sinh hoạt của người dùng.

## 22. License

Có thể sử dụng giấy phép MIT License cho mục đích học tập, nghiên cứu và phát triển tiếp.

## 23. Tác giả

- Sinh viên: Nguyễn Phi Quốc Bảo
- Đề tài: Xây dựng hệ thống hỗ trợ người cao tuổi ứng dụng thị giác máy tính Raspberry Pi 4
- Công nghệ chính: Raspberry Pi 4, Picamera2, OpenCV, YOLOv8n-Pose, Python
