#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <TinyGPS++.h>

const char* ssid = "FYP_AIOT";
const char* password = "12345678";

// Laptop Python Flask 固定 IP
const char* aiGatewayUrl =
"http://192.168.137.1:5000/upload_esp32";

// 固定 IP
IPAddress local_IP(192,168,137,88);
IPAddress gateway(192,168,137,1);
IPAddress subnet(255,255,255,0);

WebServer server(80);

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

TinyGPSPlus gps;

HardwareSerial SerialGPS(2);

float currentTemp = 0.0;
float currentHum = 0.0;

String currentLat = "2.2873";
String currentLng = "111.8305";

uint8_t* photoBuffer = NULL;
size_t photoBufferLen = 0;

void handleUpload() {

  if (photoBufferLen > 0) {

    Serial.printf(
      "Forwarding Image (%d bytes)\n",
      photoBufferLen
    );

    if (WiFi.status() == WL_CONNECTED) {

      HTTPClient http;

      http.begin(aiGatewayUrl);

      String boundary = "----ESP32Boundary";

      http.addHeader(
        "Content-Type",
        "multipart/form-data; boundary=" + boundary
      );

      String bodyStart =
        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"temp\"\r\n\r\n" +
        String(currentTemp) + "\r\n"

        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"humi\"\r\n\r\n" +
        String(currentHum) + "\r\n"

        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"lat\"\r\n\r\n" +
        currentLat + "\r\n"

        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"lng\"\r\n\r\n" +
        currentLng + "\r\n"

        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n";

      String bodyEnd =
        "\r\n--" + boundary + "--\r\n";

      size_t totalLen =
        bodyStart.length() +
        photoBufferLen +
        bodyEnd.length();

      uint8_t* totalBuf =
        (uint8_t*)malloc(totalLen);

      if (totalBuf) {

        memcpy(
          totalBuf,
          bodyStart.c_str(),
          bodyStart.length()
        );

        memcpy(
          totalBuf + bodyStart.length(),
          photoBuffer,
          photoBufferLen
        );

        memcpy(
          totalBuf + bodyStart.length() + photoBufferLen,
          bodyEnd.c_str(),
          bodyEnd.length()
        );

        int httpCode =
          http.POST(totalBuf, totalLen);

        Serial.printf(
          "AI Server Response: %d\n",
          httpCode
        );

        if (httpCode < 0) {

          Serial.println(
            http.errorToString(httpCode)
          );
        }

        free(totalBuf);

      } else {

        Serial.println(
          "Memory allocation failed"
        );
      }

      http.end();
    }

    free(photoBuffer);

    photoBuffer = NULL;
    photoBufferLen = 0;

    server.send(
      200,
      "text/plain",
      "OK"
    );

  } else {

    server.send(
      400,
      "text/plain",
      "Missing Image"
    );
  }
}

void handleFileUpload() {

  HTTPUpload& upload = server.upload();

  if (upload.status == UPLOAD_FILE_START) {

    Serial.println(
      "--- Image Upload Start ---"
    );

    if (photoBuffer) {

      free(photoBuffer);
    }

    photoBuffer =
      (uint8_t*)malloc(40000);

    if (!photoBuffer) {

      Serial.println(
        "Photo Buffer malloc failed"
      );

      return;
    }

    photoBufferLen = 0;

  } else if (
    upload.status == UPLOAD_FILE_WRITE
  ) {

    if (
      photoBufferLen + upload.currentSize
      < 40000
    ) {

      memcpy(
        photoBuffer + photoBufferLen,
        upload.buf,
        upload.currentSize
      );

      photoBufferLen += upload.currentSize;
    }

  } else if (
    upload.status == UPLOAD_FILE_END
  ) {

    Serial.printf(
      "Image received: %d bytes\n",
      photoBufferLen
    );
  }
}

void setup() {

  Serial.begin(115200);

  dht.begin();

  SerialGPS.begin(
    9600,
    SERIAL_8N1,
    16,
    17
  );

  // 固定 IP
  WiFi.config(local_IP, gateway, subnet);

  WiFi.begin(ssid, password);

  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);

  Serial.print("Connecting WiFi");

  unsigned long startAttempt = millis();

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");

    if (millis() - startAttempt > 20000) {

      Serial.println(
        "\nWiFi Failed. Restarting..."
      );

      ESP.restart();
    }
  }

  Serial.println("\nWiFi Connected");

  Serial.print("Gateway IP: ");
  Serial.println(WiFi.localIP());

  server.on(
    "/upload",
    HTTP_POST,
    handleUpload,
    handleFileUpload
  );

  server.begin();

  Serial.println(
    "Gateway Server Started"
  );
}

void loop() {

  server.handleClient();

  static unsigned long lastSensor = 0;

  if (millis() - lastSensor > 5000) {

    currentTemp =
      dht.readTemperature();

    currentHum =
      dht.readHumidity();

    if (gps.location.isValid()) {

      currentLat =
        String(gps.location.lat(), 6);

      currentLng =
        String(gps.location.lng(), 6);
    }

    lastSensor = millis();
  }

  while (SerialGPS.available()) {

    gps.encode(SerialGPS.read());
  }
}