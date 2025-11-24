from paho.mqtt import client as mqtt_client


server = '5.129.245.67'
port = 1883
topic = "python/mqtt"
client_id = 'Mixchat'
username = 'mikmaster'
password = 'mike31199'

client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)


def connection():
    client.username_pw_set(username, password)
    client.on_connect = "Connected to MQTT Broker!"
    client.connect(server, port)


def publish(msg):
    # Отправить сообщение в MQTT
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Отправлено `{msg}` в топик `{topic}`")
    else:
        print(f"Не удалось отправить сообщение в топик {topic}")
