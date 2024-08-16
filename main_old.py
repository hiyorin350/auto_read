import os
import cv2
import torch
import numpy as np
import pytesseract
from pytesseract import Output
from math import atan2, degrees, pi

# 環境変数からパスを取得（デフォルトはローカル環境のパス）
repo_path = '/Users/hiyori/autoread_dev/yolov5'
weights_path = 'yolov5/runs/train/new_meter_detection3/weights/best.pt'
image_path = '/Users/hiyori/YOLO_test/dataset/images/test/test_meter_1.jpg'

# Docker環境の場合、パスを変更
if os.path.exists('/usr/src/app/yolov5'):
    repo_path = '/usr/src/app/yolov5'
    weights_path = '/usr/src/app/yolov5/runs/train/new_meter_detection3/weights/best.pt'
    image_path = '/usr/src/app/dataset/images/test/test_meter_1.jpg'

# YOLOv5モデルのロード
model = torch.hub.load(repo_path, 'custom', path=weights_path, source='local', force_reload=True)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['KMP_INIT_AT_FORK'] = 'FALSE'
os.environ['OMP_NUM_THREADS'] = '1'

def skeletonize(image):
    size = np.size(image)
    skel = np.zeros(image.shape, np.uint8)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while True:
        eroded = cv2.erode(image, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image, temp)
        skel = cv2.bitwise_or(skel, temp)
        image = eroded.copy()

        zeros = size - cv2.countNonZero(image)
        if zeros == size:
            break

    return skel

class DegreeHistgram:
    def __init__(self):
        self.dlbl = None
        self.Rpt = (0, 0)  # 初期化
        self.Lpt = None
        self.Rmax = 0
        self.Lmax = 0
        self.lv = None
        self.tv = None
        self.maxValueP = None

    def getDistance(self, x, y, x2, y2):
        distance = np.sqrt((x2 - x) * (x2 - x) + (y2 - y) * (y2 - y))
        return distance

    def histgramMethodUzGray(self, lbl, c, s, e, l, res):
        cols = lbl.shape[1]
        rows = lbl.shape[0]

        if c[0] >= cols:
            print("正しく円が検出できていない(大きい）")
            return 0

        if c[1] >= rows:
            print("正しく円が検出できていない(大きい)")
            return 0

        self.dlbl = lbl.copy()
        Llabel = lbl[0:c[1], 0:c[0]]
        Rlabel = lbl[0:c[1], c[0]:cols]

        for row in range(Rlabel.shape[0]):
            for col in range(Rlabel.shape[1]):
                if Rlabel[row, col] == 255:
                    if row > self.Rmax:
                        self.Rmax = row
                        self.Rpt = (col, row)

        if self.Rpt is not None:
            self.Rpt = (self.Rpt[0] + c[0], self.Rpt[1] + c[1])

        for row in range(Llabel.shape[0]):
            for col in range(Llabel.shape[1]):
                if Llabel[row, col] == 255:
                    if row > self.Lmax:
                        self.Lmax = row
                        self.Lpt = (col, row)

        if self.Lpt is not None:
            self.Lpt = (self.Lpt[0], self.Lpt[1] + c[1])

        calc_hist = np.zeros((360, 360), dtype=np.uint8)
        draw_hist = np.zeros((360, 360), dtype=np.uint8)
        buf = np.zeros(360, dtype=np.int32)

        self.lv = np.array([-c[0], -c[1]])
        for row in range(rows):
            for col in range(cols):
                if lbl[row, col] == 255:
                    self.tv = np.array([col - c[0], row - c[1]])
                    inner = np.dot(self.lv, self.tv)
                    cross = np.cross(self.lv, self.tv)
                    sita = atan2(cross, inner)
                    radian = (sita * 180.0 / pi) if sita >= 0 else (sita + (2 * pi)) * 180.0 / pi
                    buf[int(radian)] += 3

        maxrad = 0
        tmpbuf = 0
        for i in range(360):
            if buf[i] >= calc_hist.shape[0]:
                buf[i] = calc_hist.shape[0] - 1
            if buf[i] > tmpbuf:
                tmpbuf = buf[i]
                maxrad = i
            calc_hist[buf[i], i] = 255
            if buf[i] > 0:
                cv2.line(draw_hist, (i, buf[i]), (i, 0), (255, 255, 255), 1, cv2.LINE_4)

        maxp = 0
        sminrad = 1000
        eminrad = 1000
        maxminrad = 1000
        for row in range(rows):
            for col in range(cols):
                if lbl[row, col] == 255:
                    self.tv = np.array([col - c[0], row - c[1]])
                    inner = np.dot(self.lv, self.tv)
                    cross = np.cross(self.lv, self.tv)
                    sita = atan2(cross, inner)
                    radian = (sita * 180.0 / pi) if sita >= 0 else (sita + (2 * pi)) * 180.0 / pi
                    if abs(radian - maxrad) < maxminrad:
                        maxminrad = abs(radian - maxrad)
                        self.maxValueP = (col, row)

        if self.Rpt[0] < self.Lpt[0]:
            self.Rpt = (self.Rpt[0] + 1, self.Rpt[1])
            self.Lpt = (self.Lpt[0] - 1, self.Lpt[1])
            s[0], s[1] = self.Rpt #FIXME?
            e[0], e[1] = self.Lpt
        else:
            self.Rpt = (self.Rpt[0] + 1, self.Rpt[1])
            self.Lpt = (self.Lpt[0] - 1, self.Lpt[1])
            #e[0], e[1] = self.Rpt "append"って一回でいいの？
            e.append(self.Rpt)
            
            #s[0], s[1] = self.Lpt
            s.append(self.Rpt)
                       

        dline = self.dlbl
        #l[0], l[1] = self.maxValueP
        l.append(self.maxValueP)
        res = draw_hist

        cv2.line(lbl, c, (l[0]), 200, thickness=2)

        return 0

# 画像のパス
# image_path = '/Users/hiyori/YOLO_test/dataset/images/test/test_meter_1.jpg'

# 画像の読み込み
image = cv2.imread(image_path)
if image is None:
    print(f"Failed to load image at path: {image_path}")
else:
    print(f"Image loaded successfully from: {image_path}")

# BGRからRGBに変換（YOLOv5はRGB画像を期待）
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 検出を行う
results = model(image_rgb)

# 検出結果の取得
detections = results.xyxy[0].cpu().numpy()

# ラベル名のマッピング
label_map = {0: 'meter', 5: 'needle', 2: 'min_value', 3: 'max_value', 4: 'unit'}

# 検出結果の格納
meter_roi = None
unit = ""
min_value = ""
max_value = ""
needle_angle = None

for detection in detections:
    x1, y1, x2, y2, confidence, class_id = detection
    class_id = int(class_id)
    if confidence > 0.4:
        if class_id in label_map:
            if label_map[class_id] == 'meter':
                meter_roi = image[int(y1):int(y2), int(x1):int(x2)]
            elif label_map[class_id] == 'unit':
                unit_roi = image[int(y1):int(y2), int(x1):int(x2)]
                unit = pytesseract.image_to_string(unit_roi, config='--psm 6').strip()
            elif label_map[class_id] == 'min_value':
                min_value_roi = image[int(y1):int(y2), int(x1):int(x2)]
                min_value = pytesseract.image_to_string(min_value_roi, config='--psm 6').strip()
            elif label_map[class_id] == 'max_value':
                max_value_roi = image[int(y1):int(y2), int(x1):int(x2)]
                max_value = pytesseract.image_to_string(max_value_roi, config='--psm 6').strip()
            elif label_map[class_id] == 'needle':
                needle_roi = image[int(y1):int(y2), int(x1):int(x2)]
                
                # ここから針の検出を行います
                gray = cv2.cvtColor(needle_roi, cv2.COLOR_BGR2GRAY)
                thres_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3)
                skeleton = skeletonize(thres_image)
                
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skeleton)
                max_width = 0
                max_width_label = -1
                for label in range(1, num_labels):
                    x, y, w, h, area = stats[label]
                    if w > max_width:
                        max_width = w
                        max_width_label = label

                max_width_region = np.zeros_like(skeleton)
                max_width_region[labels == max_width_label] = 255

                my_instance = DegreeHistgram()
                s, e, l, res = [], [], [], []
                my_instance.histgramMethodUzGray(max_width_region, [needle_roi.shape[1]//2, needle_roi.shape[0]//2], s, e, l, res)

                if res:
                    needle_angle = res[0]  # 仮に最初の結果を使用

# 結果の表示
print(f"Unit: {unit}")
print(f"Min Value: {min_value}")
print(f"Max Value: {max_value}")
if needle_angle is not None:
    print(f"Needle angle: {needle_angle:.2f} degrees")
else:
    print("Needle not detected")

# 画像の保存
# output_image_path = '/Users/hiyori/YOLO_test/images/detected/detected_meter16_aug_0.jpg'
# cv2.imwrite(output_image_path, image)
# print(f"Image saved to {output_image_path}")

# 結果の表示（任意）
cv2.imshow('Detected Analog Meters', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
