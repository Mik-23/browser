import os
import sys
import time
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

load_dotenv()


server = os.getenv('MQTT_SERVER')
port = os.getenv('MQTT_PORT')
topic = os.getenv('MQTT_ANSWER_TOPIC')
client_id = os.getenv('CLIENT_ID')
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')
msg = ''
exit_flag = False

client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic)
    print("Подключён к MQTT")


def subscribe():
    try:
        global exit_flag
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(server, int(port))
        client.loop_start()  # Запускаем цикл в фоне
        start = time.time()
        while not exit_flag:
            time.sleep(0.1)
        exit_flag = False
        print(time.time() - start)
        client.loop_stop()  # Останавливаем цикл
        client.disconnect()

    except KeyboardInterrupt:
        print("Соединение прервано")
        sys.exit()


def on_message(client, userdata, message):
    global msg, exit_flag
    msg = message.payload.decode()
    print('MQTT MESSAGE:',message.payload.decode())
    exit_flag = True
    print(f"{message.topic}: {message.payload.decode()}")


def print_message():
    print(msg)
    return msg

