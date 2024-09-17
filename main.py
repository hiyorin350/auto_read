import os
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import sys
import json
from inference_sdk import InferenceHTTPClient

def calculate_angles_and_ratios(center, start, end, tip):
    """指定された計算式を使用して、角度と割合を計算"""

    def calculate_angle_with_xy_inversion_180(center, point):
        if isinstance(center, dict) and isinstance(point, dict):
            delta_x = center.get('x', 0) - point.get('x', 0)  # X軸の反転を考慮
            delta_y = center.get('y', 0) - point.get('y', 0)  # Y軸の反転を考慮
        else:
            delta_x = center[0] - point[0]  # X軸の反転を考慮
            delta_y = center[1] - point[1]  # Y軸の反転を考慮
        angle = np.arctan2(delta_y, delta_x)
        angle_degrees = np.degrees(angle)  # 度数法での角度を返す
        
        # 角度を -180 度から 180 度の範囲に収める
        if angle_degrees > 180:
            angle_degrees -= 360
        return angle_degrees
    
    # centerと各点の間の角度を計算
    angle_start = calculate_angle_with_xy_inversion_180(center, start)
    angle_end = calculate_angle_with_xy_inversion_180(center, end)
    angle_tip = calculate_angle_with_xy_inversion_180(center, tip)

    # 提示された計算式に基づいて角度の差を計算
    total_angle = 360 + angle_end - angle_start
    tip_angle = angle_tip - angle_start
    
    # print(f"Total angle (360 + end - start): {total_angle:.2f} degrees")
    # print(f"Tip angle (tip - start): {tip_angle:.2f} degrees")
    
    # 割合を計算
    angle_ratio = tip_angle / total_angle
    # print(f"Ratio of tip angle to total angle: {angle_ratio:.2f}")

    return total_angle, tip_angle, angle_ratio

# sys.pathにyolov5を追加
sys.path.append('/app/yolov5')

# コマンドライン引数からデータを取得
image_path = sys.argv[1]
max_value = float(sys.argv[2])  # max_valueを取得し、浮動小数点に変換
min_value = float(sys.argv[3])  # min_valueを取得し、浮動小数点に変換

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

# Start, End, Center, Tipの座標を読み取る
start_prediction = best_predictions.get('Start')
end_prediction = best_predictions.get('End')
center_prediction = best_predictions.get('Center')
tip_prediction = best_predictions.get('Tip')

# 角度と割合を計算
total_angle, tip_angle, angle_ratio = calculate_angles_and_ratios(center_prediction, start_prediction, end_prediction, tip_prediction)

result_value = angle_ratio * (max_value - min_value)

# 結果をJSON形式で出力
result_json = {
    "result_value": result_value if result_value else None
}
print(json.dumps(result_json))
