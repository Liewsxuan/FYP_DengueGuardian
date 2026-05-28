#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "FYP_AIOT";
const char* password = "12345678";

// ESP32 Gateway 固定 IP
const char* gatewayUrl =
"http://192.168.137.88/upload";

// 固定 IP
IPAddress local_IP(192,168,137,89);
IPAddress gateway(192,168,137,1);
IPAddress subnet(255,255,255,0);

void setup() {

  Serial.begin(115200);

  // 固定 IP
  WiFi.config(local_IP, gateway, subnet);

  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;

  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;

  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;

  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;

  config.pin_pwdn  = 32;
  config.pin_reset = -1;

  config.xclk_freq_hz = 20000000;

  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = FRAMESIZE_QVGA;

  config.jpeg_quality = 12;

  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK) {

    Serial.printf(
      "Camera init failed: 0x%x\n",
      err
    );

    return;
  }

  WiFi.begin(ssid, password);

  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);

  Serial.print("Connecting to WiFi");

  unsigned long startAttempt = millis();

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");

    if (millis() - startAttempt > 20000) {

      Serial.println("\nWiFi Failed. Restarting...");

      ESP.restart();
    }
  }

  Serial.println("\nCamera Ready & Connected!");

  Serial.print("ESP32-CAM IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi Lost. Reconnecting...");

    WiFi.reconnect();

    delay(5000);

    return;
  }

  camera_fb_t * fb = esp_camera_fb_get();

  if (!fb) {

    Serial.println("Camera capture failed");

    delay(2000);

    return;
  }

  HTTPClient http;

  http.begin(gatewayUrl);

  String boundary = "----CAMBoundary";

  http.addHeader(
    "Content-Type",
    "multipart/form-data; boundary=" + boundary
  );

  String header =
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"image\"; filename=\"cam.jpg\"\r\n"
    "Content-Type: image/jpeg\r\n\r\n";

  String footer =
    "\r\n--" + boundary + "--\r\n";

  size_t totalLen =
    header.length() +
    fb->len +
    footer.length();

  uint8_t* postBody =
    (uint8_t*)malloc(totalLen);

  if (postBody) {

    memcpy(
      postBody,
      header.c_str(),
      header.length()
    );

    memcpy(
      postBody + header.length(),
      fb->buf,
      fb->len
    );

    memcpy(
      postBody + header.length() + fb->len,
      footer.c_str(),
      footer.length()
    );

    int code = http.POST(postBody, totalLen);

    Serial.printf(
      "Upload status: %d\n",
      code
    );

    if (code < 0) {

      Serial.println(
        http.errorToString(code)
      );
    }

    free(postBody);

  } else {

    Serial.println("Memory allocation failed");
  }

  http.end();

  esp_camera_fb_return(fb);

  delay(5000);
}