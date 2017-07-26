void setup() {
  Serial.begin(9600);
  pinMode(16, INPUT); //D0
  pinMode(5, INPUT);  //D1
}

void loop() {
  if ((digitalRead(16) == 1) || (digitalRead(5) == 1)) {
    Serial.println("Gagal");
  }
  else {
    int sensorValue = analogRead(A0);
    Serial.println(sensorValue);
  }
//  delay(1);
}
