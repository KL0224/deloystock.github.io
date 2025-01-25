from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import os 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


# Processing data
data_fpt = pd.read_csv('/var/www/html/deloystock.github.io/FPT.csv')
data_fpt['Date/Time'] = pd.to_datetime(data_fpt['Date/Time'])
data_fpt['H-L'] = data_fpt['High'] - data_fpt['Low']
data_fpt['C-O'] = data_fpt['Close'] - data_fpt['Open']

# Định nghĩa target_scaler
target_scaler = MinMaxScaler(feature_range=(0, 1))
target_scaler.fit_transform(data_fpt['Close'].values.reshape(-1, 1))

def predict_stock_price(input_date, model, data, time):
    input_date = pd.to_datetime(input_date)

    if input_date < data['Date/Time'].min() + pd.Timedelta(days=time):
        raise ValueError("Không đủ dữ liệu cho input.")

    samples = data[data['Date/Time'] < input_date].tail(time)
    samples = samples[['Open', 'High', 'Low', 'Volume', 'H-L', 'C-O']].values.reshape(-1, 6) # n mẫu mỗi mẫu 6 đặc trưng

    # Định nghĩa scaler và transform dữ liệu
    scaler = MinMaxScaler(feature_range=(0, 1))
    samples = scaler.fit_transform(samples) # fit and transform

    samples = np.array(samples)
    samples = samples.reshape(1, samples.shape[0], samples.shape[1])

    # Dự đoán kết quả
    prediction = model.predict(samples)
    prediction = target_scaler.inverse_transform(prediction) # Transform lại giá trị thực

    return prediction

app = Flask(__name__)
CORS(app)

# Load mô hình LSTM đã huấn luyện
model = tf.keras.models.load_model('/var/www/html/deloystock.github.io/model_fpt.h5')

@app.route("/")
def home():
    return send_file("index.html") # Phục vụ file html

@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.json
    input_date = input_data.get("input_date")
    
    # Gọi hàm predict_stock_price để dự đoán
    try:
        prediction = predict_stock_price(input_date, model, data_fpt, 30)  
        return jsonify({'prediction': f'{prediction}'}) # Trả về giá trị dự đoán
    except ValueError as e:
        return jsonify({'error': str(e)}), 400  # Trả về lỗi nếu không đủ dữ liệu

if __name__ == '__main__':
    app.run(host='0.0.0.0', post=5000)