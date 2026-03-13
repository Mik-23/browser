import os
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

cred_path = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
        }

try:
    # Пытаемся инициализировать Firebase
    cred = credentials.Certificate(cred_path)
    firebase_app = firebase_admin.initialize_app(cred)
    app = firebase_admin.get_app()
    print("Firebase Admin SDK успешно инициализирован!")
except Exception as e:
    print(f"Ошибка инициализации Firebase: {e}")
    firebase_app = None


def send_push_notification(fcm_token, title, body, image, data=None):
    # Отправка push-уведомления через FCM
    try:
        # Создаем сообщение
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image
            ),
            data=data or {},
            token=fcm_token,
        )
        # Отправляем
        response = messaging.send(message)
        print("Уведомление отправлено")
        return response
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return None
