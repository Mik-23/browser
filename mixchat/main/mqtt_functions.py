import os
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

load_dotenv()


server = os.getenv('MQTT_SERVER')
port = os.getenv('MQTT_PORT')
topic = os.getenv('MQTT_TOPIC')
client_id = os.getenv('CLIENT_ID')
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)


def connection():
    client.username_pw_set(username, password)
    client.on_connect = "Connected to MQTT Broker!"
    client.connect(server, int(port))


def publish(msg):
    # Отправить сообщение в MQTT
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Отправлено `{msg}` в топик `{topic}`")
    else:
        print(f"Не удалось отправить сообщение в топик {topic}")
