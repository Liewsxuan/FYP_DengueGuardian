import cv2
import numpy as np
import requests
from flask import Flask, request
from ultralytics import YOLO
import math

app = Flask(__name__)

# PocketBase 配置
PB_LOCAL_URL = "http://127.0.0.1:8090/api/collections/captures/records"

# 加载模型
try:
    model = YOLO("model/mosquito.pt")
except:
    model = YOLO("yolov8n.pt")

def clean_float(val):
    try:
        f_val = float(val)
        # 处理 NaN 或 Infinity，PocketBase 不接受这些非法数值
        if math.isnan(f_val) or math.isinf(f_val):
            return 0.0
        return f_val
    except:
        return 0.0

@app.route('/upload_esp32', methods=['POST'])
def upload_esp32():
    print("\n--- [New Request Received] ---")
    
    if 'image' not in request.files:
        print("❌ Error: No image field in request.")
        return "NO_IMAGE", 400

    img_file = request.files['image']
    temp = clean_float(request.form.get('temp', "0"))
    humi = clean_float(request.form.get('humi', "0"))
    lat = request.form.get('lat', "0")
    lng = request.form.get('lng', "0")
    
    print(f"📊 Sensors -> Temp: {temp}, Hum: {humi}, Lat: {lat}, Lng: {lng}")

    try:
        # 读取图片数据
        img_bytes = img_file.read()
        data = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ Error: Could not decode image.")
            return "DECODE_ERROR", 400
        
        img = cv2.resize(img, (640, 480))

        # YOLO 识别
        results = model(img, verbose=False)
        count = len(results[0].boxes)
        print(f"🔍 Detection Result: {count} mosquitoes found.")

        if count > 0:
            # 绘制识别框
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # 重新编码带框的图片
            _, buffer = cv2.imencode('.jpg', img)

            files = {
                'image': ('detect.jpg', buffer.tobytes(), 'image/jpeg')
            }

            payload = {
                "temperature": temp,
                "humidity": humi,
                "latitude": lat,
                "longitude": lng,
                "label": f"Mosquito count: {count}"
            }

            # 存入 PocketBase
            try:
                r = requests.post(PB_LOCAL_URL, data=payload, files=files, timeout=5)
                if r.status_code in [200, 201]:
                    print("✅ Data & Image saved to PocketBase.")
                    # ⚠️ 重要：返回给 ESP32 的指令
                    return "MOSQUITO_DETECTED", 200
                else:
                    print(f"❌ PocketBase PB Error: {r.text}")
                    return "PB_SAVE_ERROR", 500
            except Exception as e:
                print(f"❌ PocketBase Connection Error: {e}")
                return "PB_CONN_ERROR", 500

        # 如果没有识别到蚊子
        print("ℹ️ No mosquito detected in this frame.")
        return "NO_TARGET", 200

    except Exception as e:
        print(f"🔥 Processing Error: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    # 确保防火墙允许 5000 端口
    app.run(host='0.0.0.0', 
            port=5000,
            debug = False
    )