#include <Servo.h>


Servo rubiks_servo;  // create servo object to control a servo
Servo arm_servo; // create servo object for arm

int x;
int pos = 0; // Initial position for the servo
int iter = 0;
int bandera = 0;
int move_speed = 6;
int current_rubiks_pos = 0;
int pos_90_deg = 66;
int pos_180_deg = 160;
int pos_push = 15;
int i = 0;

// For Seria Data Reception
const byte numChars = 32;
char receivedChars[numChars];
String kociemba_sol = "";
//char kociemba_sol[numChars];
char caca[numChars];

boolean newData = false;

// Faces Position
int faces[] = {1, 2, 3, 4}; // For Faces {left, up, right, down}  Back and Front assummed the same

void accept_string()
{
        
        char ready_signal = 'ready';
        char received_signal = 'received';
 
        for (int piece_num = 0; piece_num <5; piece_num++)
        {       
                // send ready signal
                Serial.println(ready_signal);
                delay(100);
        }
        // receive string
        while(kociemba_sol == "")
        {
                char character;
                while(Serial.available())
                {
                    character = Serial.read();
                        kociemba_sol.concat(character);
                }
        }
       

        
        delay(10);
        Serial.print("String Aceptado: ");
       Serial.print(kociemba_sol);
 
        // send color confirmed signal
        Serial.println("arduino dice:");
        Serial.println(received_signal);
        Serial.println(kociemba_sol);
        delay(10);
}

void setup() {
  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
  //Serial.setTimeout(1);

  // Attach servo to specified pin
  arm_servo.attach(6); // pin 6 para Brazo
  rubiks_servo.attach(5); // pin 5 para cubo

  arm_servo.write(2); // Set Servo initially at 0
  rubiks_servo.write(0); // pin 5 para cubo

  // Delay during setup to be able to place the cube for test
  delay(5000);
}

void move_servo(int destination, char servo){
  if(destination > current_rubiks_pos){
    if(servo == 'r'){
      for(pos = current_rubiks_pos; pos <= destination; pos += 1){
        rubiks_servo.write(pos); // 66 for 90deg and 200 for 180deg
        delay(move_speed);
      }
    }
    else if(servo == 'a'){
      for(pos = current_rubiks_pos; pos <= destination; pos += 1){
        arm_servo.write(pos); // 66 for 90deg and 200 for 180deg
        delay(move_speed);
      }
    }
    
  }

  else if(destination < current_rubiks_pos){
    if(servo == 'r'){
      for(pos = current_rubiks_pos; pos >= destination; pos -= 1){
        rubiks_servo.write(pos); // 66 for 90deg and 200 for 180deg
        delay(move_speed);
      }
    }
    else if(servo == 'a'){
      for(pos = current_rubiks_pos; pos >= destination; pos -= 1){
        arm_servo.write(pos); // 66 for 90deg and 200 for 180deg
        delay(move_speed);
      }
    }

  }
  
  // Updating current rubiks cube position
  current_rubiks_pos = destination;
  delay(2000); // delay 500ms
}

// Push Cube Forward to flip it
void flip(){
  arm_servo.write(35);
  delay(1500); // delay 500ms
  arm_servo.write(0); // regresamos a base
  delay(2000);
}


void girar_cubo_90d_CW(){
  rubiks_servo.write(pos_90_deg); // the exact value to rotate 90deg is 66 in the servo write 
  delay(2000); // delay 500ms

}

void girar_cubo_180d_CW(){
  rubiks_servo.write(pos_180_deg); // the exact value to rotate 180deg is 160 in the servo write 
  delay(2000); // delay 500ms

}



void cubo_home(){
  rubiks_servo.write(0);
  delay(2000);
}

void shift_positions(int shift_value){
  int tmp_value_face;
  for(i = 0; i < 4; i++){
    tmp_value_face = faces[i];
    if(shift_value != 0){
      tmp_value_face += shift_value;
      // Restart face counter
      if(tmp_value_face > 4){
        tmp_value_face = (tmp_value_face-4);
      }
      // Update Face Value Cas
      faces[i] = tmp_value_face;

    }
    
    //Serial.println(tmp_value_face);
  }
}

void spin_right(int num_giros){
  // Girar Cubo 90 grados
  move_servo(pos_90_deg, 'r');
  flip();
  flip();
  flip();
  //cubo_home();
  if(num_giros == 1){ // Right Side queda desfazado 1 cara
    cubo_home();
    rotate_lower_face_90d();
    // Put Front face on top again
    flip();
    flip();
    flip();
    // Update face position
    cubo_home();
    shift_positions(3);

  }

  else if(num_giros == 2){ // Right Side queda desfazado 1 cara
    cubo_home();
    rotate_lower_face_180d();
    move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    flip();
    flip();

    // Update face position
    cubo_home();
    shift_positions(2);

  }

  else if(num_giros == 3){ // Right Side queda desfazado 3 cara
  
    cubo_home();
    rotate_lower_face_180d();
    cubo_home();
    rotate_lower_face_90d();
    // Put Front face on top again
    flip();

    // Update face position
    cubo_home();
    shift_positions(1);
  }
  

}

void spin_up(int num_giros){
  flip();
  if(num_giros == 1){ // sin desfase
    rotate_lower_face_90d();
    move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    flip();
    flip();
    cubo_home();
    // Update face position
    shift_positions(3);

  }

  else if(num_giros == 2){ 
    rotate_lower_face_180d();
    // Put Front face on top again
    flip();
    cubo_home();
    // Update face position
    shift_positions(2);

  }

  else if(num_giros == 3){ //  Desfasado 2 posiciones
  
    rotate_lower_face_180d();
    rotate_lower_face_90d();
    move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    cubo_home();
    // Update face position
    shift_positions(1);

  }

}


void spin_down(int num_giros){
  flip();
  flip();
  flip();
  if(num_giros == 1){ // sin desfase
    rotate_lower_face_90d();
    move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    cubo_home();
    // Update face position
    shift_positions(3);
  }

  else if(num_giros == 2){ //  Desfasado 2 posiciones
    rotate_lower_face_180d();
    // Put Front face on top again
    flip();
    flip();
    flip();
    cubo_home();
    // Update face position
    shift_positions(2);

  }

  else if(num_giros == 3){ //  Desfasado 2 posiciones
  
    rotate_lower_face_180d();
    rotate_lower_face_90d();
    move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    flip();
    flip();
    cubo_home();
    // Update face position
    shift_positions(1);

  }

}

void spin_back(int num_giros){
  if(num_giros == 1){ // sin desfase
    rotate_lower_face_90d();
    cubo_home();
    // Update face position
    shift_positions(3);
  }

  else if(num_giros == 2){ //  Desfasado 2 posiciones
    rotate_lower_face_180d();
    cubo_home();
    // Update face position
    shift_positions(2);

  }

  else if(num_giros == 3){ //  Desfasado 2 posiciones
  
    rotate_lower_face_180d();
    rotate_lower_face_90d();
    cubo_home();
    // Update face position
    shift_positions(1);

  }

}

void spin_front(int num_giros){
  cubo_home();
  flip();
  flip();
  if(num_giros == 1){ // sin desfase
    rotate_lower_face_90d();
    // Put Front face on top again
    flip();
    flip();
    cubo_home();
    shift_positions(1);
  }

  else if(num_giros == 2){ //  Desfasado 2 posiciones
    rotate_lower_face_180d();
    // Put Front face on top again
    flip();
    flip();
    cubo_home();
    // Update face position
    shift_positions(2);

  }

  else if(num_giros == 3){ //  Desfasado 2 posiciones
  
    rotate_lower_face_180d();
    rotate_lower_face_90d();
    // Put Front face on top again
    flip();
    flip();
    cubo_home();
    // Update face position
    shift_positions(3);

  }

}


void spin_left(int num_giros){
  // Girar Cubo 90 grados
  move_servo(pos_90_deg, 'r');
  flip();
  //cubo_home();
  if(num_giros == 1){ // Right Side queda desfazado 1 cara
    cubo_home();
    rotate_lower_face_90d();
    // Put Front face on top again
    flip();
    cubo_home();
    // Update face position
    shift_positions(3);

  }

  else if(num_giros == 2){ // Right Side queda desfazado 1 cara
    cubo_home();
    rotate_lower_face_180d();
    // Put Front face on top again
    move_servo(pos_90_deg, 'r');
    flip();


    cubo_home();
    // Update face position
    shift_positions(2);

  }

  else if(num_giros == 3){ // Right Side queda desfazado 3 cara
  
    cubo_home();
    rotate_lower_face_180d();
    rotate_lower_face_90d();
    //move_servo(pos_90_deg, 'r');
    // Put Front face on top again
    flip();
    flip();
    flip();

    cubo_home();
    // Update face position
    shift_positions(1);
  }
  

}

// Sping Upper Part CW
void rotate_lower_face_90d(){
  arm_servo.write(pos_push);
  delay(2000); // delay 500ms
  // Girar Cubo
  move_servo(120, 'r'); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms
  move_servo(30, 'r'); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms

  move_servo(90, 'r'); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms

  move_servo(65, 'r'); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms

  // Regreso Brazo
  arm_servo.write(2); // regresamos a base
  delay(2000);  
  move_servo(0, 'r');
  delay(2000);
}

void rotate_lower_face_180d(){
  arm_servo.write(pos_push);
  delay(2000); // delay 500ms
  move_servo(180, 'r');
  move_servo(150, 'r');
  // Girar Cubo
  /*
  rubiks_servo.write(180); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms
  rubiks_servo.write(90); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms

  rubiks_servo.write(150); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms

  rubiks_servo.write(122); // the exact value to rotate 90deg is 66 in the servo write however we'll try 90 to spin it completely in the cube
  delay(2000); // delay 500ms
  */

  // Regreso Brazo
  arm_servo.write(2); // regresamos a base
  delay(2000);  
  rubiks_servo.write(0);
  delay(2000);
}

// based on where each one of the faces are, rotate the accordingly
void rotate_correct_face(char selector,int num_rotations){
  int face_location;
  // Switch form the rest other than Fron and Back, front and back are constantly in the correct place
  // To find the index in the array based on what we want
  switch (selector){
        case 'L':
          face_location = faces[0];
          break;
        case 'U':
          face_location = faces[1];
          break;
        case 'R':
          face_location = faces[2];
          break;
        case 'D':
          face_location = faces[3];
          break;
  }
  // Getting the location of the face and where is it nnow  
  switch (face_location){
    // Face 1 es left
    case 1:
        spin_left(num_rotations);
      break;
    case 2:
        spin_up(num_rotations);
      break;
    case 3:
        spin_right(num_rotations);
      break;
    case 4:
        spin_down(num_rotations);
      break;
  }
}

void loop() {
  int demo = 3;

  // Read all string
  if(demo == 1){
    
    
  } // end of else if

 

  else if (demo == 2){
    
    while (Serial.available() == 0) {} 
    String caca = Serial.readString();
    
    if(caca[0] == 'x'){
      Serial.println(caca);
      //spin_right(3);
      spin_back(3);
      //rotate_lower_face_180d();
    }

    
  }
  else if (demo==3){
    recvWithStartEndMarkers();
    showNewData();
    // run_fullMethod();
  }

} // end of void loop()

void recvWithStartEndMarkers() {
    // Mark that we are receiving characters
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }

}

void showNewData() {
    if (newData == true) {
        Serial.print("The Solution is ... ");
        Serial.println(receivedChars);
        delay(5000);
        // Attach servo to specified pin
        arm_servo.attach(6); // pin 6 para Brazo
        rubiks_servo.attach(5); // pin 5 para cubo
      
        arm_servo.write(2); // Set Servo initially at 0
        rubiks_servo.write(0); // pin 5 para cubo
        run_fullMethod();
        newData = false;
    }
}

void run_fullMethod(){
  //while ((Serial.available() == 0)||(bandera==1)) {} 
    // kociemba_sol = "F1B1U2D2F2B2U2D2";
    kociemba_sol = String(receivedChars);

    //while (Serial.available() == 0) {} 
    //kociemba_sol = Serial.readString();
    
    //accept_string();
    // Read String
    //String res = Serial.readString();
    // Store length of string
    int str_length = kociemba_sol.length();

    
    
    // Index Separation
    int idx_ini = 0;
    int idx_fin = 2;
    // Each pair of digits is the number of movements    
    int num_movements = str_length / 2;
    Serial.print("Num Mov: ");
    Serial.println(num_movements);

    
    // Iterate through each one of the movements sent serially from Raspberry Pi
    for (int i = 0; i < num_movements; i++){
      // Read Substring 
      String tmp_str = kociemba_sol.substring(idx_ini, idx_fin);
      // Rotation Indication
      int rotation = 0;
      // Traditionally 1, 2 and 3 are for 90, 180 and 270 degree CW turns. I have configured te turn counterclowise
      // Because of These if we have:
      // 3 CW = 1 CCW
      // 2 CW = 2 CCW
      // 1 CW = 3 CCW

      // Determine the face to spin
      Serial.println(tmp_str);    
      Serial.println(i);

      switch(tmp_str[1]){
        case '3':
          rotation = 1;
          break;
        case '2':
          rotation = 2;
          break;
        case '1':
          rotation = 3;
          break;
      }
      
      switch (tmp_str[0]){
        case 'F':
          spin_front(rotation);
          break;
        case 'B':
          spin_back(rotation);
          break;
        default:
          rotate_correct_face(tmp_str[0], rotation);
          break;
      }
      
      
        
      // Add index for substring
      idx_ini += 2;
      idx_fin += 2;

    // Movement based on the String Read
    //if(tmp_str == "U8"){
    //  arm_servo.write(180);
      
    } // end of for for printing
    bandera = 1;
    kociemba_sol = "";
  
}
