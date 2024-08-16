from flask import Flask, request, send_file
from flask_cors import CORS  # CORSのインポート
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from io import BytesIO
from main import *

app = Flask(__name__)
CORS(app)  # CORSを適用

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# @app.route('/', methods=['GET', 'POST'])
# def html():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return 'ファイルがリクエストに含まれていません'
#         file = request.files['file']
#         if file.filename == '':
#             return 'ファイルが選択されていません'
#         if file:
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
            
#             processed_image = process_img(file_path) 
            
#             _, img_encoded = cv2.imencode('.png', processed_image)
#             img_byte_arr = BytesIO(img_encoded)
            
#             return send_file(img_byte_arr, mimetype='image/png')
    
#     return '''
#     <!doctype html>
#     <title>AutoRead</title>
#     <h1>AutoRead</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=アップロード>
#     </form>
#     '''

@app.route('/upload', methods=['GET', 'POST'])  # ルートの変更
def upload_file():
    if 'file' not in request.files:
        print("aaa")
        return {'message': 'ファイルがリクエストに含まれていません'}, 400
    file = request.files['file']
    if file.filename == '':
        print("bbb")
        return {'message': 'ファイルが選択されていません'}, 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # 画像処理
    try:
        processed_image = process_img(file_path)
        _, img_encoded = cv2.imencode('.png', processed_image)
        img_byte_arr = BytesIO(img_encoded)
        return send_file(img_byte_arr, mimetype='image/png')
    except Exception as e:
        return {'message': f'画像処理中にエラーが発生しました: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
