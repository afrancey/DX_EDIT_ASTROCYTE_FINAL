
// System Info
int NumSphereUnits = 12;

// TEENSY IDENTIFIERS
// teensy_identifiers[i] = id of node in S(1+i)
 
long int center_teensy_identifiers[12] = {258684, 258595, 245689, 245734, 245702, 258613, 258941, 245688, 258631,  258907, 245667, 245735};
long int perimeter_teensy_identifiers[12] = {245753, 245744, 258663, 259514, 258640, 248880, 245686, 258677, 258698, 245527, 258970, 258686};

int RS_pins[6] = {3,4,25,32,9,10};

// Teensy ID
// filled with read_EE(), read_teensyID()
static uint8_t teensyID[8];
long int myID;


// node number
uint8_t my_number;

int TESTPIN_LED = 13;

void setup() {
  Serial.begin(57600);
  myID = read_teensyID();
  my_number = get_my_number(myID);
  
  for (int i = 0; i < 6; i++){
    pinMode(RS_pins[i], OUTPUT);
  }

  delay(1000);


}

void loop() {

  // see if we are receiving a message
  uint8_t incomingByte;
  uint8_t commandByte = 0xff;

  if (Serial.available() > 3){
    
    incomingByte = Serial.read();

    if (incomingByte == commandByte){

      uint8_t incomingNumber = Serial.read();
      uint8_t incomingPin = Serial.read();
      uint8_t testpin = 0x19;
      uint8_t incomingValue = Serial.read();

      if (incomingNumber == my_number){
        analogWrite(incomingPin, incomingValue);
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
