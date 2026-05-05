#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --------- LCD ---------
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --------- DHT11 ---------
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --------- Ultrasonic ---------
#define TRIG_PIN 5
#define ECHO_PIN 6

// --------- Soil Sensor ---------
#define SOIL_PIN A0

// --------- LoRa Pins ---------
#define SS 10
#define RST 9
#define DIO0 2

void setup() {
  Serial.begin(9600);

  // LCD setup
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Flood Monitor");
  delay(2000);
  lcd.clear();

  // DHT setup
  dht.begin();

  // Ultrasonic
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // LoRa setup
  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(433E6)) {
    lcd.print("LoRa Failed!");
    while (1);
  }

  lcd.print("LoRa Ready");
  delay(2000);
  lcd.clear();
}

// --------- Ultrasonic ---------
long readWaterLevel() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout added
  long distance = duration * 0.034 / 2;

  return distance;
}

void loop() {

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  long water = readWaterLevel();
  int soil = analogRead(SOIL_PIN);

  // --------- Handle sensor error ---------
  if (isnan(temp) || isnan(hum)) {
    Serial.println("DHT Error!");
    return;
  }

  // --------- Serial Output ---------
  Serial.print("T:"); Serial.print(temp);
  Serial.print(" H:"); Serial.print(hum);
  Serial.print(" W:"); Serial.print(water);
  Serial.print(" S:"); Serial.println(soil);

  // --------- LCD Display (No flicker) ---------
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temp);
  lcd.print(" H:");
  lcd.print(hum);

  lcd.setCursor(0, 1);
  lcd.print("W:");
  lcd.print(water);
  lcd.print(" S:");
  lcd.print(soil);

  // --------- LoRa Send ---------
  LoRa.beginPacket();
  LoRa.print(temp);
  LoRa.print(",");
  LoRa.print(hum);
  LoRa.print(",");
  LoRa.print(water);
  LoRa.print(",");
  LoRa.print(soil);
  LoRa.endPacket();

  Serial.println("Data Sent");

  delay(3000);
}