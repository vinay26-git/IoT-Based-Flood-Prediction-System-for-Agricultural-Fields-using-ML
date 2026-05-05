from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time
import requests
import csv
import os
import joblib
import numpy as np

# --------- ThingSpeak ---------
THINGSPEAK_API = "T30N64145WCUBZTC"

# --------- CSV file ---------
CSV_FILE = "flood_data.csv"

# --------- Load ML Model ---------
model = joblib.load("flood_model.pkl")

# Create file if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Temperature", "Humidity", "Water_Level", "Soil", "Flood"])

BOARD.setup()

class LoRaReceiver(LoRa):
    def __init__(self):
        super(LoRaReceiver, self).__init__()
        self.set_mode(MODE.SLEEP)
        self.set_freq(433.0)
        self.set_bw(BW.BW125)
        self.set_spreading_factor(7)
        self.set_coding_rate(CODING_RATE.CR4_5)
        self.set_preamble(8)
        self.set_sync_word(0x34)
        self.set_dio_mapping([0] * 6)

    def start(self):
        print("Receiver Started")
        self.set_mode(MODE.RXCONT)

        while True:
            flags = self.get_irq_flags()

            if flags['rx_done']:
                payload = self.read_payload(nocheck=True)
                data = bytes(payload).decode()
                print("Received:", data)

                try:
                    # Expected format: temp,hum,level,soil
                    temp, hum, level, soil = map(float, data.split(","))

                    # -------- ML Prediction --------
                    pred = model.predict(np.array([[temp, hum, level, soil]]))[0]
                    print("Flood Prediction:", pred)

                    # -------- Upload to ThingSpeak --------
                    url = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API}&field1={temp}&field2={hum}&field3={level}&field4={soil}&field5={pred}"
                    requests.get(url)
                    print("Uploaded to ThingSpeak")

                    # -------- Save in CSV --------
                    with open(CSV_FILE, mode="a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            temp, hum, level, soil, pred
                        ])
                    print("Saved in CSV")

                except Exception as e:
                    print("Error:", e)

                self.clear_irq_flags(RxDone=1)

            time.sleep(0.5)

lora = LoRaReceiver()
lora.start()