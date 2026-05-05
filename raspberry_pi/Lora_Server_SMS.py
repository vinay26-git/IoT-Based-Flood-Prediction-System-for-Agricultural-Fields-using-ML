from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time, csv, requests, joblib, numpy as np
import serial
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# -------- Load ML Model --------
model = joblib.load("flood_model.pkl")

# -------- ThingSpeak --------
THINGSPEAK_API = "T30N64145WCUBZTC"

# -------- GSM --------
PHONE = "+919347574356"

# Initialize GSM once (IMPORTANT)
gsm = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
time.sleep(2)

def send_sms(msg):
    try:
        gsm.write(b'AT+CMGF=1\r')
        time.sleep(1)
        gsm.write(f'AT+CMGS="{PHONE}"\r'.encode())
        time.sleep(1)
        gsm.write(msg.encode())
        gsm.write(b"\x1A")
        time.sleep(3)
        print("SMS Sent")
    except Exception as e:
        print("SMS Error:", e)

BOARD.setup()

class LoRaReceiver(LoRa):
    def __init__(self):
        super().__init__()
        self.set_mode(MODE.SLEEP)
        self.set_freq(433.0)
        self.set_bw(BW.BW125)
        self.set_spreading_factor(7)
        self.set_sync_word(0x34)

    def start(self):
        print("System Ready")
        self.set_mode(MODE.RXCONT)

        while True:
            flags = self.get_irq_flags()

            if flags['rx_done']:
                data = bytes(self.read_payload(nocheck=True)).decode()
                print("Received:", data)

                try:
                    temp, hum, level, soil = map(float, data.split(","))

                    # -------- ML Prediction --------
                    pred = model.predict(np.array([[temp, hum, level, soil]]))[0]
                    print("Flood:", pred)

                    # -------- Upload to ThingSpeak --------
                    url = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API}&field1={temp}&field2={hum}&field3={level}&field4={soil}&field5={pred}"
                    requests.get(url)
                    print("Uploaded to ThingSpeak")

                    # -------- GSM Alert --------
                    if pred == 1:
                        send_sms("FLOOD ALERT! Water level high.")

                except Exception as e:
                    print("Format error:", e)

                self.clear_irq_flags(RxDone=1)

            time.sleep(0.5)

LoRaReceiver().start()