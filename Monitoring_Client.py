import paho.mqtt.client as mqtt
import json

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_STATUS = "farm/monitoring/status"
CLIENT_ID = "StatusClient"

# Callback saat terhubung ke broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC_STATUS)
    else:
        print(f"Failed to connect, return code {rc}")

# Callback saat pesan diterima
def on_message(client, userdata, msg):
    try:
        # Decode pesan dan parsing JSON
        status_data = json.loads(msg.payload.decode())
        
        # Tampilkan status kandang
        print(f"Status Kandang: {status_data['status']}")
        
        # Tampilkan status kipas dan lampu tambahan
        print(f"Status Kipas: {status_data['fan_status']}")
        print(f"Status Lampu Tambahan: {status_data['lamp_status']}")
        
        # Tampilkan tindakan yang dilakukan jika ada
        if status_data["actions"]:
            print("Tindakan yang dilakukan:")
            for action in status_data["actions"]:
                print(f"- {action}")
        else:
            print("Tidak ada tindakan yang diperlukan.")
        
        print()
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
