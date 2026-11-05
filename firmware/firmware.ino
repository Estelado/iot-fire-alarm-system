#include <WiFi.h>
#include <HTTPClient.h>

// --- НАСТРОЙКИ (ЗАМЕНИТЕ НА СВОИ) ---
const char* ssid = "YOUR_WIFI_SSID";         // Имя вашей Wi-Fi сети
const char* password = "YOUR_WIFI_PASSWORD"; // Пароль от Wi-Fi
const char* serverUrl = "http://YOUR_SERVER_IP/api/data/"; // IP вашего сервера

// Пины для датчиков
#define PIN_A1 36
#define PIN_A3 39
#define PIN_A5 34

// Базовые (фоновые) значения
int baseline[3] = {0, 0, 0};

void setup() {
  Serial.begin(115200);
  
  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\nWiFi connected");

  // Калибровка фона (10 измерений)
  for (int i = 0; i < 10; i++) { 
    baseline[0] += analogRead(PIN_A1); 
    baseline[1] += analogRead(PIN_A3); 
    baseline[2] += analogRead(PIN_A5); 
    delay(50); 
  }
  baseline[0] /= 10; 
  baseline[1] /= 10; 
  baseline[2] /= 10; 
}

void loop() {
  // Чтение датчиков и вычитание фона
  int raw1 = analogRead(PIN_A1);
  int raw3 = analogRead(PIN_A3);
  int raw5 = analogRead(PIN_A5);
  
  int val1 = (raw1 - baseline[0] > 0) ? raw1 - baseline[0] : 0;
  int val3 = (raw3 - baseline[1] > 0) ? raw3 - baseline[1] : 0;
  int val5 = (raw5 - baseline[2] > 0) ? raw5 - baseline[2] : 0;

  // Проверка порога (600 ед. АЦП)
  bool fire = (val1 > 600 || val3 > 600 || val5 > 600);
  
  String direction = "";
  if (val1 > 600) direction += "A1(left) ";
  if (val3 > 600) direction += "A3(center) ";
  if (val5 > 600) direction += "A5(right) ";
  if (direction == "") direction = "none";

  // Формирование JSON
  String json = "{\"device_id\":1,\"fire_alert\":" + String(fire ? "true" : "false") +
                ",\"channel_a1\":" + String(val1) + 
                ",\"channel_a3\":" + String(val3) + 
                ",\"channel_a5\":" + String(val5) + 
                ",\"direction\":\"" + direction + "\"}";

  // Отправка на сервер
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(json);
    
    if (httpCode > 0) {
      Serial.printf("HTTP %d\n", httpCode);
    } else {
      Serial.println("Error on HTTP request");
    }
    http.end();
  }
  
  // ВАЖНО: В учебном прототипе используется delay. 
  // Для реального продакшена здесь нужен esp_deep_sleep_start() для экономии энергии.
  delay(10000); // Отправка каждые 10 секунд
}
