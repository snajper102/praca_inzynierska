import requests
import random
import time
from datetime import datetime, timezone

# 1) Konfiguracja
USERNAME    = "admin"                 # Twój superużytkownik
PASSWORD    = "admin"    # Hasło admina
TOKEN_URL   = "http://localhost:8000/api-token-auth/"
READINGS_URL = "http://localhost:8000/api/admin/sensor/readings/"
SENSOR_ID   = "1"               # Musi istnieć w bazie

# 2) Pobierz token
resp = requests.post(TOKEN_URL, json={
    "username": USERNAME,
    "password": PASSWORD
})
resp.raise_for_status()
token = resp.json().get("token")
print("Uzyskany token:", token)

HEADERS = {
    "Authorization": f"Token {token}"
}

# 3) Generator fałszywych odczytów
def generate_fake_reading(sensor_id):
    return {
        "sensor_id": sensor_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "voltage": round(random.uniform(220.0, 240.0), 2),
        "current": round(random.uniform(0.5, 10.0), 2),
        "power":   round(random.uniform(100.0, 2000.0), 2),
        "energy":  round(random.uniform(0.1, 50.0), 2),
        "frequency": round(random.uniform(49.5, 50.5), 2),
        "pf":      round(random.uniform(0.8, 1.0), 2),
    }

# 4) Pętla wysyłająca dane
def send_readings():
    while True:
        reading = generate_fake_reading(SENSOR_ID)
        print("Wysyłanie:", reading)
        r = requests.post(READINGS_URL, json=[reading], headers=HEADERS)
        if r.status_code == 201:
            print("✅ OK")
        else:
            print("❌ Błąd:", r.status_code, r.text)
        time.sleep(5)

if __name__ == "__main__":
    send_readings()