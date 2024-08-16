from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="YLvLVWRClFL19rfrnakb"
)

result = CLIENT.infer('/Users/hiyori/YOLO_test/dataset/images/test/test_meter_1.jpg', model_id="gauge-meter-detection-v2/5")
# print(result)

# クラスごとに最も信頼度が高いものを選ぶ
best_predictions = {}
for prediction in result['predictions']:
    class_name = prediction['class']
    if class_name not in best_predictions or prediction['confidence'] > best_predictions[class_name]['confidence']:
        best_predictions[class_name] = prediction

# 抽出された結果をクラス名と座標の形式で出力
coordinates_with_class = [(pred['class'], pred['x'], pred['y']) for pred in best_predictions.values()]
print(coordinates_with_class)