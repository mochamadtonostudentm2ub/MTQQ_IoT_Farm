import paho.mqtt.client as mqtt
import json

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SENSOR = "farm/monitoring/sensors"
TOPIC_STATUS = "farm/monitoring/status"
CLIENT_ID = "Controller"

# Ambang batas sensor
THRESHOLDS = {
    "temperature": {"min": 20.0, "max": 35.0},  # Suhu (°C)
    "humidity": {"min": 40.0, "max": 70.0},     # Kelembapan (%)
    "co2": {"min": 300.0, "max": 600.0},        # CO2 (ppm)
    "ammonia": {"min": 0.0, "max": 25.0}        # Gas amonia (ppm)
}

# Status kontrol perangkat
fan_status = "OFF"
lamp_status = "OFF"

# Callback saat terhubung ke broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC_SENSOR)
    else:
        print(f"Failed to connect, return code {rc}")

# Callback saat pesan diterima
def on_message(client, userdata, msg):
    global fan_status, lamp_status
    try:
        # Decode pesan dan parsing JSON
        sensor_data = json.loads(msg.payload.decode())
        print(f"Sensor data received: {sensor_data}")

        status = "Kandang Stabil"
        actions = []

        # Evaluasi kipas (berdasarkan suhu, amonia, dan CO2)
        if (
            sensor_data["temperature"] > THRESHOLDS["temperature"]["max"] or
            sensor_data["ammonia"] > THRESHOLDS["ammonia"]["max"] or
            sensor_data["co2"] > THRESHOLDS["co2"]["max"]
        ):
            if fan_status == "OFF":
                actions.append("Menyalakan kipas untuk menstabilkan suhu, amonia, atau CO2")
                fan_status = "ON"
            status = "Kandang Tidak Stabil"
        else:
            if fan_status == "ON":
                actions.append("Mematikan kipas karena suhu, amonia, dan CO2 normal")
                fan_status = "OFF"

        # Evaluasi lampu tambahan (berdasarkan kelembapan)
        if sensor_data["humidity"] > THRESHOLDS["humidity"]["max"]:
            if lamp_status == "OFF":
                actions.append("Menyalakan lampu tambahan untuk mengurangi kelembapan")
                lamp_status = "ON"
            status = "Kandang Tidak Stabil"
        else:
            if lamp_status == "ON":
                actions.append("Mematikan lampu tambahan karena kelembapan normal")
                lamp_status = "OFF"

        # Kirim status ke Subscriber
        message = {
            "status": status,
            "fan_status": fan_status,
            "lamp_status": lamp_status,
            "actions": actions
        }
        client.publish(TOPIC_STATUS, json.dumps(message))
        print(f"Published status: {message}")

    except Exception as e:
        print(f"Error processing message: {e}")

# Inisialisasi MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Koneksi ke broker MQTT
try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except Exception as e:
    print(f"Failed to connect to broker: {e}")
