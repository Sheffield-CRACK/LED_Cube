//Pin connected to ST_CP of 74HC595
int latchPin = 5;
//Pin connected to SH_CP of 74HC595
int clockPin = 3;
//Pin connected to DS of 74HC595
int dataPin = 2;

int oePin = 6;
int mrPin = 4;

// How many 74hct595 are in cascade
const int N_REGISTERS = 8;

// How long to illuminate each layer
const int FLASH_PERIOD = 3;

// Layer counter
int layer = 0;

// For recieving data
byte recieved = 0;
int last_layer_recieved = 0;
int BAUDRATE = 9600;

// This array actually does the legwork
byte cube[N_REGISTERS*N_REGISTERS];

// Initial state
char initial[8*N_REGISTERS*N_REGISTERS] = {
        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '1', '1', '1', '1', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '1', '1', '1', '1', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '0', '1', '1', '0', '0', '0',
        '0', '0', '0', '1', '1', '0', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '0', '1', '1', '0', '0', '0',
        '0', '0', '0', '1', '1', '0', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '1', '1', '1', '1', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '1', '0', '0', '1', '0', '0',
        '0', '0', '1', '1', '1', '1', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',

        '1', '0', '0', '0', '0', '0', '0', '1',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '1', '0', '0', '0', '0', '0', '0', '1',
};

void setup() {
  // set pins to output because they are 
  // addressed in the main loop
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(clockPin, OUTPUT);

  pinMode(mrPin, OUTPUT);
  pinMode(oePin, OUTPUT);
  

  digitalWrite(oePin, LOW);
  digitalWrite(mrPin, HIGH);
  digitalWrite(clockPin, LOW);
  
  Serial.begin(BAUDRATE);
  Serial.write("I've been reset...\n");
  
  char2binary();
}

void loop() {
  if (Serial.available()) recieveBytes();
  
  writeLayer(layer);
  
  // Iterate up through the layers
  layer += 1;
  layer = layer % N_REGISTERS;
}


// Convert the initial state to the binary arrays
void char2binary(){
  // Convert the layer to it's binary representation
  for (int i=0; i<N_REGISTERS*N_REGISTERS; i++){
    // Reset the row to all off
    cube[i] = 0;
    
    // Loop through this layer and convert to binary
    cube[i] += initial[8*i] - 48;
    for (int j=1; j<8; j++){
      cube[i] <<= 1;
      cube[i] += initial[8*i + j] - 48;
    }
  }
}

void addressLayer(int layer){
  registerWrite(layer, true);
}

void registerWrite(int whichPin, int whichState) {
// the bits you want to send
  byte bitsToSend = 0;

  // turn off the output so the pins don't light up
  // while you're shifting bits:
  digitalWrite(latchPin, LOW);

  // turn on the next highest bit in bitsToSend:
  bitWrite(bitsToSend, whichPin, whichState);

  // shift the bits out:
  shiftOut(dataPin, clockPin, LSBFIRST, bitsToSend);
}


// Shove the rows array out to the shift registers
void writeLayer(int mylayer){
  // Write the rows to the registers
  // Disable pushing the output
  digitalWrite(latchPin, false);
  
  // Address the desired layer
  registerWrite(mylayer, true);
  
  // Push the rows of the layer out
  for (int i=mylayer*N_REGISTERS; i<(1+mylayer)*N_REGISTERS; i++){
    shiftOut(dataPin, clockPin, LSBFIRST, cube[i]);
  }
  
  // Push the output
  digitalWrite(latchPin, true);
}


// Recieve all the bytes that were pushed across 
// and push them into the layers array
void recieveBytes(){
  while(Serial.available()){
    recieved = Serial.read();
    
//    Serial.print("Recieved: ");
//    Serial.println(recieved, BIN);

    cube[last_layer_recieved] = recieved;
    last_layer_recieved++;
    last_layer_recieved = last_layer_recieved % (N_REGISTERS*N_REGISTERS);
  }
}
