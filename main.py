import os
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import sys
import json
from inference_sdk import InferenceHTTPClient

# sys.pathにyolov5を追加
sys.path.append('/app/yolov5')

# コマンドライン引数からデータを取得
image_path = sys.argv[1]

try:
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="YLvLVWRClFL19rfrnakb"
    )
except Exception as e:
    print(json.dumps({"error": f"モデルのロード中にエラーが発生しました: {e}"}))
    sys.exit(1)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['KMP_INIT_AT_FORK'] = 'FALSE'
os.environ['OMP_NUM_THREADS'] = '1'

result = CLIENT.infer(image_path, model_id="gauge-meter-detection-v2/5")

# 画像の読み込み
image = cv2.imread(image_path)
if image is None:
    print(json.dumps({"error": f"Failed to load image at path: {image_path}"}))
    sys.exit(1)

# クラスごとに最も信頼度が高いものを選ぶ
best_predictions = {}
for prediction in result['predictions']:
    class_name = prediction['class']
    if class_name not in best_predictions or prediction['confidence'] > best_predictions[class_name]['confidence']:
        best_predictions[class_name] = prediction

# StartとEndの値を読み取る
start_prediction = best_predictions.get('Start')
end_prediction = best_predictions.get('End')

# OCRを適用して数値を読み取る関数
def apply_ocr_on_prediction(image, prediction):
    if prediction:
        x, y, width, height = int(prediction['x']), int(prediction['y']), int(prediction['width']), int(prediction['height'])
        region = image[y:y+height, x:x+width]
        
        # 前処理: グレースケール化と閾値処理
        gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, thresh_region = cv2.threshold(gray_region, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Tesseract OCRで数値のみを読み取る
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'
        text = pytesseract.image_to_string(thresh_region, config=custom_config).strip()
        
        # 数値のみを抽出
        numeric_text = ''.join(filter(lambda c: c.isdigit() or c == '.', text))
        return numeric_text
    else:
        return None

# StartとEndにOCRを適用
start_text = apply_ocr_on_prediction(image, start_prediction)
end_text = apply_ocr_on_prediction(image, end_prediction)

# 結果をJSON形式で出力
result_json = {
    "Start": start_text if start_text else None,
    "End": end_text if end_text else None
}
print(json.dumps(result_json))
