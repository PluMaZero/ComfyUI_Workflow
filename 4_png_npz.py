import numpy as np
from PIL import Image
import cv2
from ultralytics import YOLO  # 👈 객체 인식을 위한 YOLO 라이브러리 추가

input_path = r"F:\Military.png"
output_path = r"F:\Military_multiband.npz"

# 1️⃣ 이미지 로드
img = Image.open(input_path).convert("RGB")
img_np = np.array(img).astype(np.float32) / 255.0
H, W, _ = img_np.shape

# 2️⃣ RGB → (3, H, W)
rgb = np.transpose(img_np, (2, 0, 1))
channel_names = ["img_01_r", "img_01_g", "img_01_b"]

# 3️⃣ 객체 감지 및 마스크 생성 (YOLOv8 Segmentation 사용)
print("객체 인식 모델을 로드하고 분석 중입니다...")
# 'yolov8n-seg.pt'는 가장 가볍고 빠른 분할 모델입니다. (처음 실행 시 자동 다운로드 됨)
model = YOLO("yolov8n-seg.pt") 

# 이미지에서 객체 추론 (img를 numpy uint8 형태로 전달하는 것이 정확도에 좋음)
img_for_yolo = cv2.cvtColor((img_np * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
results = model(img_for_yolo)

masks_list = []

# 감지된 객체(마스크)가 있는지 확인
if results[0].masks is not None:
    # 텐서 데이터를 numpy 배열로 변환
    masks_data = results[0].masks.data.cpu().numpy()  # 형태: (객체수, H', W')
    class_ids = results[0].boxes.cls.cpu().numpy().astype(int) # 감지된 클래스 ID
    class_dict = results[0].names # 클래스 이름 사전 (0: person, 2: car 등)

    for i, (mask, cls_id) in enumerate(zip(masks_data, class_ids)):
        # YOLO가 출력한 마스크 해상도가 원본과 다를 수 있으므로 원본(W, H)에 맞게 리사이즈
        mask_resized = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)
        masks_list.append(mask_resized)
        
        # 채널 이름 동적 할당 (예: mask_person_01, mask_car_02)
        obj_name = class_dict[cls_id]
        channel_names.append(f"mask_{obj_name}_{i+1:02d}")

# 4️⃣ RGB + masks 결합
if len(masks_list) > 0:
    masks_np = np.stack(masks_list)  # (N, H, W)
    all_channels = np.concatenate([rgb, masks_np], axis=0)
else:
    print("감지된 객체가 없습니다. RGB 채널만 저장합니다.")
    all_channels = rgb

# 5️⃣ batch 차원 추가
all_channels = all_channels[np.newaxis, :, :, :]

# 6️⃣ 저장 (Comfy Multiband 형식)
np.savez_compressed(
    output_path,
    multiband=all_channels,
    channel_names=np.array(channel_names)
)

print("\n✅ 완료:", output_path)
print("✅ Shape:", all_channels.shape)
print("✅ Channels:", channel_names)