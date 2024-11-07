#include "DHT.h"
#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

// Init

#define DHTPIN 4
#define BUZZERPIN 8
#define RELAYPIN 7
#define DHTTYPE DHT11

// Color sensor pin definitions (adjust as needed)
#define S0 9
#define S1 10
#define S2 11
#define S3 12
#define OUT 13

#define POX_PERIOD_MS     1000
#define TEMP_PERIOD_MS    1500  // Reading temperature every 1.5 seconds

uint32_t tsLastPoxReport = 0;
uint32_t tsLastTempReport = 0;

PulseOximeter pox;
DHT dht(DHTPIN, DHTTYPE);

bool is_arrhythmia = false;
bool prev_status = true;
float bpm = 0;
float spo2 = 0;
float temperature = 0;

void readTemp() {
  if (millis() - tsLastTempReport > TEMP_PERIOD_MS) {
    temperature = dht.readTemperature();
    tsLastTempReport = millis();
  }

}



void checkArrhythmia(float bpm) {
  const int min_rate = 60;
  const int max_rate = 120;

  is_arrhythmia = (bpm >= max_rate || bpm <= min_rate);
  if (is_arrhythmia) {
   if(prev_status != is_arrhythmia){
     prev_status = is_arrhythmia;
     Serial.println("Shock Delivered");
   }
   digitalWrite(RELAYPIN, LOW);
  } else {
  
    prev_status = false;
    
    digitalWrite(RELAYPIN, HIGH);
  }
}


void printValues() {
  Serial.print("temp : ");
  Serial.print(temperature);
  Serial.print(" bpm : ");
  Serial.println(bpm);
  Serial.print(" Arrhithmea : ");
  Serial.println(is_arrhythmia);
}

void readPox() {
  pox.update();
  if (millis() - tsLastPoxReport > POX_PERIOD_MS) {
    bpm = pox.getHeartRate();
    checkArrhythmia(bpm);
    tsLastPoxReport = millis();
    printValues();
  } 
}

void onBeatDetected() {
  // Callback for when a beat is detected
}

void setup() {
  Serial.begin(9600);

  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(OUT, INPUT);

  pinMode(RELAYPIN, OUTPUT);

  // digitalWrite(MOTOR, HIGH);

  digitalWrite(S0, HIGH);
  digitalWrite(S1, HIGH);

  dht.begin();
  pox.begin();
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  pox.setOnBeatDetectedCallback(onBeatDetected);
}

void loop() {
  readTemp();
  readPox();
  
  
}
