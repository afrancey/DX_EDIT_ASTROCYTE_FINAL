#include <SoftPWM.h>

// System Info
int NumSphereUnits = 12;

// TEENSY IDENTIFIERS
// teensy_identifiers[i] = id of node in S(1+i)
 
long int center_teensy_identifiers[12] = {258684, 258595, 245689, 245734, 245702, 258613, 258941, 245688, 258631,  258907, 245667, 245735};
long int perimeter_teensy_identifiers[12] = {245753, 245744, 258663, 259514, 258640, 248880, 245686, 258677, 258698, 245527, 258970, 258686};

int RS_pins[6] = {3,4,25,32,9,10};

                    //center              
int moth_pins[10] = {9, 10, 22, 23, 29, 30, 22, 20, 6, 16};

int SoftPWM_pins[3] = {29, 30, 16};

int sampling_rate = 100;
long last_sample_time = millis();
int IR_pin = 17;
int IR_threshold = 1100;
bool IR_sampling_on = false;

long last_message_time = millis();
long idle_wait_time = 30000; //2 seconds
bool idle_state = false;
int idle_state_stage = 0;
int max_brightness = 50;
bool idle_increasing = true;
int idle_rate = 100;
long last_stage_change = millis();
long idle_random_light = random(3);
long idle_random_moth_1 = random(6);
long idle_random_moth_2 = random(6);
bool idling_on = true;

// Teensy ID
// filled with read_EE(), read_teensyID()
static uint8_t teensyID[8];
long int myID;
int my_type; //0 = center, 1 = perimeter


// node number
uint8_t my_number;

int TESTPIN_LED = 13;

bool serial_on = true;

void setup() {
  SoftPWMBegin(SOFTPWM_NORMAL);
  Serial.begin(57600);
  myID = read_teensyID();
  my_number = get_my_number(myID);
  my_type = get_my_type(myID);

  if (my_type == 1){
    for (int i = 0; i < 6; i++){
      pinMode(RS_pins[i], OUTPUT);
    }
  } else {
    for (int i = 0; i < 10; i++){
      pinMode(moth_pins[i], OUTPUT);
    }
  }

  pinMode(IR_pin, INPUT);

  delay(1000);

  last_sample_time = millis();
  last_message_time = millis();

  


}

void loop() {


  if (millis() - last_message_time > idle_wait_time && idling_on){
    if (millis() - last_stage_change > idle_rate){
      last_stage_change = millis();

      if (idle_state_stage <= max_brightness){

        if (my_type == 1){
          safe_write(RS_pins[idle_random_light*2], idle_state_stage);
        } else {
          safe_write(moth_pins[idle_random_moth_1], idle_state_stage);
          safe_write(moth_pins[idle_random_moth_2], idle_state_stage);
        }
      }

      if (idle_state_stage == 0){      
        idle_increasing = true;
        idle_random_light = random(3);
        idle_random_moth_1 = random(6);
        idle_random_moth_2 = random(6);
      } else if (idle_state_stage == 50) {
        idle_increasing = false;
      }
      
  
      if (idle_increasing){
        idle_state_stage++;
      } else {
        idle_state_stage--;
      }
    }
    
  }

  // see if we are receiving a message
  uint8_t incomingByte;
  uint8_t commandByte = 0xff;
  int IR_val;
  

  if (Serial.available() > 3 && serial_on){
    
    incomingByte = Serial.read();

    if (incomingByte == commandByte){

      uint8_t incomingNumber = Serial.read();
      uint8_t incomingPin = Serial.read();
      uint8_t testpin = 0x19;
      uint8_t incomingValue = Serial.read();

      if (incomingNumber == my_number){

        last_message_time = millis();
        safe_write(incomingPin, incomingValue);
      }

     }

    }

    if (IR_sampling_on){
      if (my_number == 1 || my_number == 4 || my_number == 7 || my_number == 10){
        IR_val = analogRead(IR_pin);
        if (IR_val > IR_threshold){
          Serial.write(0xff);
        }
      }
    }


 

}


// Code to read the Teensy ID
void read_EE(uint8_t word, uint8_t *buf, uint8_t offset) {
  noInterrupts();
  FTFL_FCCOB0 = 0x41;             // Selects the READONCE command
  FTFL_FCCOB1 = word;             // read the given word of read once area

  // launch command and wait until complete
  FTFL_FSTAT = FTFL_FSTAT_CCIF;
  while (!(FTFL_FSTAT & FTFL_FSTAT_CCIF));
  *(buf + offset + 0) = FTFL_FCCOB4;
  *(buf + offset + 1) = FTFL_FCCOB5;
  *(buf + offset + 2) = FTFL_FCCOB6;
  *(buf + offset + 3) = FTFL_FCCOB7;
  interrupts();
}

long int read_teensyID() {
  read_EE(0xe, teensyID, 0); // should be 04 E9 E5 xx, this being PJRC's registered OUI
  read_EE(0xf, teensyID, 4); // xx xx xx xx
  myID = (teensyID[5] << 16) | (teensyID[6] << 8) | (teensyID[7]);
  return myID;
}

int get_my_number(long int myID){
  uint8_t my_number;
  uint8_t my_type;

  // first check centre spars
  for (uint8_t unit = 0x00; unit < NumSphereUnits; unit+= 0x01){
    if (center_teensy_identifiers[unit] == myID){
      my_number = unit;
      Serial.print(unit);
    }
    if (perimeter_teensy_identifiers[unit] == myID){
      my_number = unit + 12;
      Serial.print(unit);
    }
  }

  return my_number;
}

int get_my_type(long int myID){
  int my_type;

  // first check centre spars
  for (uint8_t unit = 0x00; unit < NumSphereUnits; unit+= 0x01){
    if (center_teensy_identifiers[unit] == myID){
      my_type = 0;
      Serial.print(unit);
    }
    if (perimeter_teensy_identifiers[unit] == myID){
      my_type = 1;
      Serial.print(unit);
    }
  }

  return my_type;
}

void safe_write(uint8_t incomingPin, uint8_t val){

  uint8_t incomingValue;

  if (val > 50){
    incomingValue = 0;
  } else {
    incomingValue = val;
  }
  
  if (incomingPin == SoftPWM_pins[0] || incomingPin == SoftPWM_pins[1] || incomingPin == SoftPWM_pins[2]){
    SoftPWMSet(incomingPin, incomingValue);
  } else {
    analogWrite(incomingPin, incomingValue);
  }
  
}
