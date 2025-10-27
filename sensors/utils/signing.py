import hmac
import hashlib
from django.conf import settings

def sign_data(value, timestamp):
    # Zakładamy, że timestamp to string w formacie ISO z dokładnością do sekund
    message = f"{value}-{timestamp}".encode('utf-8')
    secret = settings.SENSOR_DATA_SECRET.encode('utf-8')
    signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
    return signature

def verify_signature(value, timestamp, signature):
    expected = sign_data(value, timestamp)
    return hmac.compare_digest(expected, signature)