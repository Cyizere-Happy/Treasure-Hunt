/*
 * Arduino Bluetooth Joystick Controller for 3D Robot
 * 
 * Joystick Power is hardcoded to come from Pin 9 (acts as 5V output)
 * Bluetooth baud rate set to 38400
 */

#include <SoftwareSerial.h>

// Bluetooth module pins
#define BT_RX 10  // Connect to TX of HC-05
#define BT_TX 11  // Connect to RX of HC-05 (use voltage divider!)

// Joystick pins
#define JOY_X A1
#define JOY_Y A2
#define JOY_BTN 2

// Button pins
#define JUMP_BTN 3
#define WAVE_BTN 4
#define DANCE_BTN 5

// Joystick Power Pin (hardcoded)
#define JOY_POWER A0   // Provides 5V to the joystick

// Joystick calibration
#define JOY_CENTER 512
#define JOY_DEADZONE 100
#define JOY_THRESHOLD 300

// Timing
#define COMMAND_DELAY 300
#define DEBOUNCE_DELAY 50

// Create software serial for Bluetooth
SoftwareSerial BTSerial(BT_RX, BT_TX);

// Button state tracking
bool jumpBtnLastState = HIGH;
bool waveBtnLastState = HIGH;
bool danceBtnLastState = HIGH;
bool joyBtnLastState = HIGH;

unsigned long lastJumpPress = 0;
unsigned long lastWavePress = 0;
unsigned long lastDancePress = 0;
unsigned long lastJoyPress = 0;
unsigned long lastCommandTime = 0;

// Movement state
String lastCommand = "";

void setup() {
  // Initialize serial communications
  Serial.begin(9600);          // For debugging via Serial Monitor
  BTSerial.begin(38400);       // Bluetooth baud rate set to 38400
  
  // Power the joystick from pin 9
  pinMode(JOY_POWER, OUTPUT);
  digitalWrite(JOY_POWER, HIGH);  // Supply 5V to joystick module

  // Configure button pins with internal pull-up resistors
  pinMode(JOY_BTN, INPUT_PULLUP);
  pinMode(JUMP_BTN, INPUT_PULLUP);
  pinMode(WAVE_BTN, INPUT_PULLUP);
  pinMode(DANCE_BTN, INPUT_PULLUP);

  // LED indicator
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println("3D Robot Bluetooth Controller Initialized");
  Serial.println("Bluetooth baud rate: 38400");
  Serial.println("Joystick powered via Pin 9 (5V output). Waiting for connection...");

  // Blink LED to show ready
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
}

void loop() {
  int xValue = analogRead(JOY_X);
  int yValue = analogRead(JOY_Y);

  int xDiff = xValue - JOY_CENTER;
  int yDiff = yValue - JOY_CENTER;

  String command = "";

  // Movement detection
  if (abs(xDiff) > JOY_DEADZONE || abs(yDiff) > JOY_DEADZONE) {
    if (abs(yDiff) > abs(xDiff)) {
      if (yDiff > JOY_THRESHOLD) command = "forward";
      else if (yDiff < -JOY_THRESHOLD) command = "backward";
    } else {
      if (xDiff > JOY_THRESHOLD) command = "rotate_right";
      else if (xDiff < -JOY_THRESHOLD) command = "rotate_left";
    }
  }

  if (command != "" && command != lastCommand) {
    if (millis() - lastCommandTime >= COMMAND_DELAY) {
      sendCommand(command);
      lastCommand = command;
      lastCommandTime = millis();
    }
  } else if (command == "") {
    lastCommand = "";
  }

  // Check jump, wave, dance, and joystick buttons
  checkButton(JUMP_BTN, &jumpBtnLastState, &lastJumpPress, "jump");
  checkButton(WAVE_BTN, &waveBtnLastState, &lastWavePress, "wave");
  checkButton(DANCE_BTN, &danceBtnLastState, &lastDancePress, "dance");
  checkButton(JOY_BTN, &joyBtnLastState, &lastJoyPress, "reset");

  delay(50);
}

void checkButton(int pin, bool *lastState, unsigned long *lastPress, String cmd) {
  bool currentState = digitalRead(pin);
  if (currentState == LOW && *lastState == HIGH) {
    if (millis() - *lastPress > DEBOUNCE_DELAY) {
      sendCommand(cmd);
      *lastPress = millis();
      blinkLED();
    }
  }
  *lastState = currentState;
}

void sendCommand(String cmd) {
  BTSerial.println(cmd);
  Serial.print("Sent command: ");
  Serial.println(cmd);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);
}

void blinkLED() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
}