import os
import time
import sys
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from .cifer import gen_key, decrypt_text


load_dotenv()
salt = os.getenv('CIFER_SALT')


class MQTT:
    def __init__(self, mqtt_dict, client, user_id, exit_flag, msg):
        key = gen_key(user_id, salt)
        self.client = client
        self.exit_flag = exit_flag
        self.msg = msg
        self.server = decrypt_text(mqtt_dict[f'server_{user_id}'], key).decode('utf-8')
        self.port = mqtt_dict[f'port_{user_id}']
        self.mqtt_username = decrypt_text(mqtt_dict[f'mqtt_username_{user_id}'], key).decode('utf-8')
        self.mqtt_password = decrypt_text(mqtt_dict[f'mqtt_password_{user_id}'], key).decode('utf-8')
        self.topic_sent = mqtt_dict[f'topic_sent_{user_id}']
        self.topic_subscribe = mqtt_dict[f'topic_subscribe_{user_id}']

    def connection(self):
        self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        # self.client.on_connect = "Connected to MQTT Broker!"
        if self.server and self.port:
            self.client.connect(self.server, int(self.port))
            print("Connect to server")
        else:
            print("Ошибка отправки. Не верные данные сервера")

    def publish(self, msg):
        # Отправить сообщение в MQTT
        if self.topic_sent:
            result = self.client.publish(self.topic_sent, msg)
            status = result[0]
            if status == 0:
                print(f"Отправлено `{msg}` в топик `{self.topic_sent}`")
            else:
                print(f"Не удалось отправить сообщение в топик {self.topic_sent}")
        else:
            print("Ошибка. Неверный топик для отправки")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic_subscribe)
        else:
            print("Failed to connect, return code %d\n", rc)

    def subscribe(self):
        try:
            if self.server and self.port:
                self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
                self.client.on_connect = self.on_connect
                self.client.on_message = self.on_message
                self.client.connect(self.server, int(self.port))
                self.client.loop_start()  # Запускаем цикл в фоне
                start = time.time()
                while not self.exit_flag:
                    time.sleep(0.1)
                self.exit_flag = False
                print(time.time() - start)
                self.client.loop_stop()  # Останавливаем цикл
                print(self.client.is_connected)
                self.client.disconnect()
            else:
                print("Ошибка получения. Не верные данные сервера")

        except KeyboardInterrupt:
            print("Соединение прервано")
            sys.exit()

    def on_message(self, client, userdata, message):
        self.msg = message.payload.decode()
        print('MQTT MESSAGE:', message.payload.decode())
        self.exit_flag = True

    def print_message(self):
        print(self.msg)
        return self.msg


def return_mqtt(mqtt_dict, user_id):
    mqtt = MQTT(mqtt_dict, mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,
                mqtt_dict[f'client_id_{user_id}']), user_id,False, '')
    return mqtt
