const int GREENLEDS1[] = {22, 23, 24, 25, 26, 27};
const int REDLEDS1[] = {2, 29, 30, 31, 32, 33};

const int GREENLEDS2[] = {40, 42, 43, 44, 45, 47};
const int REDLEDS2[] = {36, 37, 38, 39, 41};

const int buttonPin = 52;  // Pin for the push button
int buttonState = 0;       // Variable to store the button state

void setup() {
  // Initialize LED pins as outputs
  for (int i = 0; i < 6; i++) {
    pinMode(GREENLEDS1[i], OUTPUT);
    pinMode(REDLEDS1[i], OUTPUT);
  }
  for (int i = 0; i < 5; i++) {
    pinMode(REDLEDS2[i], OUTPUT);
  }
  for (int i = 0; i < 6; i++) {
    pinMode(GREENLEDS2[i], OUTPUT);
  }

  // Initialize the button pin as an input
  pinMode(buttonPin, INPUT_PULLUP);

  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Check if there is any incoming serial command
  if (Serial.available() > 0) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');
    
    // Process the command
    command.trim(); // Remove any leading/trailing whitespace
    
    if (command == "SEQ1") {
      // Command to activate ledseq1 (GREENLEDS1 on, REDLEDS1 off, GREENLEDS2 off, REDLEDS2 on)
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS1[i], HIGH);
        digitalWrite(REDLEDS1[i], LOW);
      }
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS2[i], LOW);
      }
      for (int i = 0; i < 5; i++) {
        digitalWrite(REDLEDS2[i], HIGH);
      }
    } else if (command == "SEQ2") {
      // Command to activate ledseq2 (GREENLEDS1 off, REDLEDS1 on, GREENLEDS2 on, REDLEDS2 off)
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS1[i], LOW);
        digitalWrite(REDLEDS1[i], HIGH);
      }
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS2[i], HIGH);
      }
      for (int i = 0; i < 5; i++) {
        digitalWrite(REDLEDS2[i], LOW);
      }
    } else if (command == "IDLE") {
      // Command to go to idle state (GREENLEDS1 on, REDLEDS1 off, GREENLEDS2 off, REDLEDS2 off)
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS1[i], HIGH);
        digitalWrite(REDLEDS1[i], LOW);
      }
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS2[i], LOW);
      }
      for (int i = 0; i < 5; i++) {
        digitalWrite(REDLEDS2[i], LOW);
      }
    } else if (command == "OFF") {
      // Command to turn off all LEDs explicitly
      for (int i = 0; i < 6; i++) {
        digitalWrite(GREENLEDS1[i], LOW);
        digitalWrite(REDLEDS1[i], LOW);
        digitalWrite(GREENLEDS2[i], LOW);
      }
      for (int i = 0; i < 5; i++) {
        digitalWrite(REDLEDS2[i], LOW);
      }
    }
  }

  // Check the state of the push button
  buttonState = digitalRead(buttonPin);
  
  // If the button is pressed (LOW because of the pull-up resistor)
  if (buttonState == LOW) {
    // Send a "RESET" command
    Serial.println("RESET");
    // Reset all LEDs to the initial state
    for (int i = 0; i < 6; i++) {
      digitalWrite(GREENLEDS1[i], LOW);
      digitalWrite(REDLEDS1[i], LOW);
      digitalWrite(GREENLEDS2[i], LOW);
    }
    for (int i = 0; i < 5; i++) {
      digitalWrite(REDLEDS2[i], LOW);
    }

    // Wait until the button is released to avoid multiple triggers
    while (digitalRead(buttonPin) == LOW) {
      delay(10); // Small delay for debounce
    }
  }
}