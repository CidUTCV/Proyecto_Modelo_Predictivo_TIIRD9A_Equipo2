#include <SoftwareSerial.h>
#include <AltSoftSerial.h>

// Configuración para el sensor Winsen usando SoftwareSerial
SoftwareSerial WinsenSerial(4, 3); // RX, TX

// Configuración para el módulo SIM808 usando AltSoftSerial
AltSoftSerial SIM808; // RX, TX están predefinidos en la biblioteca

void setup() {
  Serial.begin(9600); // Comunicación serial para salida
  Serial.println("Iniciando...");

  WinsenSerial.begin(9600); // Inicializa el sensor Winsen
  SIM808.begin(9600);       // Inicializa el módulo SIM808
  
  // Inicializa el módulo SIM808
  SIM808.println("AT+CGPSPWR=1"); // Activa el GPS
  delay(2000);
}

void loop() {
  // Leer datos del sensor Winsen
  if (read_winsen()) {
    Serial.println("Datos del sensor Winsen leídos correctamente");
  } else {
    Serial.println("Error al leer el sensor Winsen");
  }

  delay(5000); // Espera antes de leer del módulo SIM808

  // Leer datos del módulo SIM808
  if (read_gps()) {
    Serial.println("Datos del GPS recibidos");
  } else {
    Serial.println("Error al leer el GPS");
  }

  delay(5000); // Espera antes de repetir
}

bool read_winsen() {
  const uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
  WinsenSerial.write(cmd, sizeof(cmd));

  unsigned long startMillis = millis();
  while (millis() - startMillis < 2000) { // Espera hasta 2 segundos para recibir datos
    if (WinsenSerial.available() >= 26) {
      byte s[26];
      for (int i = 0; i < 26; i++) {
        s[i] = WinsenSerial.read();
      }

      int pm1 = s[2] * 256 + s[3];
      int pm25 = s[4] * 256 + s[5];
      int pm10 = s[6] * 256 + s[7];
      int co2 = s[8] * 256 + s[9];
      int voc = s[10];
      float temp = ((s[11] * 256 + s[12]) - 435) * 0.1;
      float rh = s[13] * 256 + s[14];
      float ch2o = (s[15] * 256 + s[16]) * 0.001;
      float co = (s[17] * 256 + s[18]) * 0.1;
      float o3 = (s[19] * 256 + s[20]) * 0.01;
      float no2 = (s[21] * 256 + s[22]) * 0.01;

      Serial.print("");
      Serial.print(co2);
      Serial.print(", ");
      Serial.print(voc);
      Serial.print(", ");
      Serial.print(temp);
      Serial.print(", ");
      Serial.print(rh);
      Serial.print(", ");
      Serial.print(ch2o);
      Serial.print(", ");
      Serial.print(co);
      Serial.print(", ");
      Serial.print(o3);
      Serial.print(", ");
      Serial.print(no2);
      Serial.print(", ");
      Serial.print(pm1);
      Serial.print(", ");
      Serial.print(pm25);
      Serial.print(", ");
      Serial.println(pm10);

      return true; // Datos leídos correctamente
    }
    delay(100);
  }
  return false; // No se obtuvieron datos en el tiempo esperado
}

bool read_gps() {
  SIM808.println("AT+CGPSINF=0");
  delay(1000); // Espera a que se obtengan los datos

  unsigned long startMillis = millis();
  while (millis() - startMillis < 2000) { // Espera hasta 2 segundos para recibir datos
    while (SIM808.available()) {
      Serial.write(SIM808.read());
    }
    return true;
  }
  return false; // No se obtuvieron datos en el tiempo esperado
}
