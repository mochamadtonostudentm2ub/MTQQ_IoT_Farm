import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SENSOR = "farm/monitoring/sensors"
CLIENT_ID = "SensorPublisher"

# Fungsi untuk membuat data sensor secara acak
def generate_sensor_data():
    return {
        "timestamp": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        "temperature": round(random.uniform(15.0, 40.0), 2),  # Suhu dalam derajat Celcius
        "humidity": round(random.uniform(30.0, 80.0), 2),    # Kelembapan dalam persen
        "co2": round(random.uniform(2000.0, 8000.0), 2),       # CO2 dalam ppm
        "ammonia": round(random.uniform(0.0, 50.0), 2)       # Gas amonia dalam ppm
    }

# Callback saat terhubung ke broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

# Inisialisasi MQTT client
client = mqtt.Client()
client.on_connect = on_connect

# Koneksi ke broker MQTT
try:
    client.connect(BROKER, PORT, 60)
except Exception as e:
    print(f"Failed to connect to broker: {e}")
    exit()

# Loop untuk mengirimkan data secara periodik
client.loop_start()
try:
    while True:
        sensor_data = generate_sensor_data()
        client.publish(TOPIC_SENSOR, json.dumps(sensor_data))
        print(f"Published sensor data: {sensor_data}")
        time.sleep(5)  # Delay sebelum mengirim data berikutnya
except KeyboardInterrupt:
    print("Stopping simulation...")
finally:
    client.loop_stop()
    client.disconnect()
