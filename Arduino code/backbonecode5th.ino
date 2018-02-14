#include <NewPing.h>
#include <Servo.h>
#define sensor A8

Servo watertap;
Servo front;


const int brki=22,brkj=25,rmot=23,lmot=24,rpwm=2,lpwm=3;  // create servo object to control a servo
//const int rencode=35,lencode=31;
const int brkf=26,fmot=28;
int irl = 38,irr = 39,irb=40;
int speedl=50,speedr=48,debouncetime=10;





// defines variables
long traveltime;
int distance;
unsigned long time;
int waterpos = 90,frontpos = 90;
String str;
int pwm, duration;
int hasObstacle = HIGH;
int dir = 0;


void setup() {
  
  Serial.begin(9600);
  pinMode(brki, OUTPUT);
  pinMode(brkj, OUTPUT);
  pinMode(brkf, OUTPUT);
  pinMode(rmot, OUTPUT);
  pinMode(lmot, OUTPUT);
  pinMode(fmot, OUTPUT);
  //pinMode(dmot, OUTPUT);
  pinMode(rpwm, OUTPUT);
  pinMode(lpwm, OUTPUT);
 // pinMode(rencode, INPUT);
 // pinMode(lencode, INPUT);
  digitalWrite(brki, HIGH);
  digitalWrite(brkj, HIGH);
  digitalWrite(brkf, LOW);
  digitalWrite(lmot, HIGH);
  digitalWrite(rmot, HIGH);
  digitalWrite(fmot, HIGH);
  //digitalWrite(dmot, HIGH);
  pinMode(A8,INPUT);
  pinMode(irl, INPUT);
  pinMode(irr, INPUT);
  pinMode(irb, INPUT);
   watertap.attach(7); 
   watertap.write(waterpos); 
   front.attach(6); 
   front.write(frontpos); 
     delay(100);
  while(Serial.available()==0){ //waiting here till the first command from laptop comes here
  } 
 // Serial.println("void setup ended"); 
}


void leftrotate(int x,int duration=300)
{
  time = millis();
  speedl=x;
  speedr=x;
  digitalWrite(rmot, HIGH);
  digitalWrite(lmot, LOW);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  closewater();
  Serial.println("leftrotating");
  while ( (millis() - time)<duration )
  {
    if(irsensl() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     Serial.println("Danger");
      }
  }
  
  stopbot();
  Serial.println("Next command"); 
  
}

void rightrotate(int x,int duration =300)
{
  time = millis();
  speedl=x;
  speedr=x;
  digitalWrite(rmot, LOW);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  closewater();
  Serial.println("rightrotating");
  while ( (millis() - time) < duration )
  {
    if(irsensr() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     Serial.println("Danger");
      }
  }
  
  stopbot();
  Serial.println("Next command"); 
}

void forward(int duration,int speedl=50 , int speedr = 46)
{ 
  if(pingcheck() ==1)
  {
     stopbot();
     Serial.println("danger");
     return;
    }
  
  time = millis();
 //speedl=50;
 // speedr=46;
  digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  digitalWrite(brkf, HIGH);
  openwater();
  
  Serial.println("moving forward");
  
  //checking every thing while moving
  while ( (millis() - time)<duration )
  {
    if(pingcheck() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     Serial.println("Danger");
     return;
      }
      if(irsensr() == 1 )
    {
     digitalWrite(rmot, HIGH);
  digitalWrite(lmot, LOW);
  analogWrite(rpwm, 50);
  analogWrite(lpwm, 50);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
delay(300);
duration =duration +300;
     Serial.println("left adjusted");
     digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
      }
      if(irsensl() == 1 )
    {
     digitalWrite(rmot, LOW);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, 50);
  analogWrite(lpwm, 50);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  delay(300);
  duration =duration +300;
     Serial.println("right adjusted");
     digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
      }
    }

  stopbot();
  closewater();
  Serial.println("Next command");  
  return;
}
void backward(int duration)
{
  speedl=50;
  speedr=48;
  digitalWrite(rmot, LOW);
  digitalWrite(lmot, LOW);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
   digitalWrite(brkf, HIGH);
  openwater();
  Serial.println("moving backward");
  delay(duration);
  stopbot();
  closewater();
}
void stopbot()
{
  digitalWrite(brki, HIGH);
  digitalWrite(brkj, HIGH);
  digitalWrite(brkf, LOW);
//  digitalWrite(brkd, HIGH);
  Serial.println("stopped");
  delay(10);
  
}
void rightcheck()
{ 
  time = millis();
  speedl=50;
  speedr=48;
  digitalWrite(rmot, LOW);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  Serial.println("rotating to right check");
   while ( (millis() - time) < 1000)
  {
    if(irsensr() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     Serial.println("Danger");
      }
  }
  //closewater();
  stopbot();
}
void leftcheck()
{ 
  time = millis();
  speedl=50;
  speedr=48;
  digitalWrite(rmot, HIGH);
  digitalWrite(lmot, LOW);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  Serial.println("rotating to left check");
   while ( (millis() - time) < 1000)
  {
    if(irsensl() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     Serial.println("Danger");
      }
  }
  stopbot();
}
void openwater()
{
  int waterpos = watertap.read();
  for (waterpos = waterpos; waterpos >= 0; waterpos -= 5) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    watertap.write(waterpos);              // tell servo to go to position in variable 'pos'
    delay(20); 
  }
}
void closewater(){
  int waterpos = watertap.read();
  for (waterpos = waterpos; waterpos <= 90; waterpos += 5) 
  { watertap.write(waterpos);              // tell servo to go to position in variable 'pos'
    delay(20); 
  }
}
 
int pingcheck( ) 
{ float volts = analogRead(sensor)*0.0048828125;  // value from sensor * (5/1024)
  int distance = 13*pow(volts, -1); // worked out from datasheet graph
  //Serial.println(distance);
  if (distance!=0 && distance < 7)
  {
    return 1;
    }
  else 
  {
    return 0;
    }
  }
int pingchecknew( ) 
{ float volts = analogRead(sensor)*0.0048828125;  // value from sensor * (5/1024)
  int distance = 13*pow(volts, -1); // worked out from datasheet graph
  //Serial.println(distance);
  if (distance!=0 && distance < 5)
  {
    return 1;
    }
  else 
  {
    return 0;
    }
  }

int irsensl()
{
  if ( digitalRead(irl)== LOW)
  {
  return 1;
  }
  else
  {
    return 0;
    }//temporarily made 1 i.e. always a floor detected
  }
int irsensr()
{
   if ( digitalRead(irr)== LOW)
  {
  return 1;
  }
  else
  {
    return 0;
    }
  }
int irsens()
{
   if ( digitalRead(irb)== LOW)
  {
  return 1;
  }
  else
  {
    return 0;
    }
  }

void flushinput()
{
  while(Serial.available() > 0) 
  {
    char t = Serial.read();
  }
  }
void cleanT()
  {
  //Developed by Venky
  
  }

void AllignP()
  {
    frontpos = 90;
    front.write(90);
    delay(25);
    float d=200;
    int ang;
    for (frontpos = frontpos; frontpos <= 180; frontpos += 1) 
  { 
    front.write(frontpos);
    delay(20); 
    //cal-pingvalue
    float volts = analogRead(sensor)*0.0048828125;  // value from sensor * (5/1024)
    int distance = 13*pow(volts, -1); // worked out from datasheet graph
    Serial.println("");
    Serial.print("distance = ");
    Serial.print(distance);
    Serial.print(" at angle = ");
    Serial.println(frontpos);
    if (distance <= d && distance != 0)
    {
      d = distance;
      ang = front.read();
      
      }   
  } 
for (frontpos = frontpos; frontpos >= 0; frontpos -= 1) 
  { 
    front.write(frontpos);
    delay(20); 
    //cal-pingvalue
    float volts = analogRead(sensor)*0.0048828125;  // value from sensor * (5/1024)
  int distance = 13*pow(volts, -1); // worked out from datasheet graph
    Serial.println("");
    Serial.print("distance = ");
    Serial.print(distance);
    Serial.print(" at angle = ");
    Serial.print(frontpos);
    if (distance <= d&& distance != 0)
    {
      d = distance;
      ang = front.read();
      }   
  }
for (frontpos = frontpos; frontpos <= 90; frontpos += 1) 
  { 
    front.write(frontpos);
    delay(20); 
    //cal-pingvalue
    float volts = analogRead(sensor)*0.0048828125;  // value from sensor * (5/1024)
  int distance = 13*pow(volts, -1); // worked out from datasheet graph    Serial.println("");
    Serial.print("distance = ");
    Serial.print(distance);
    Serial.print(" at angle = ");
    Serial.println(frontpos);
    if (distance <=d && distance != 0)
    {
      d = distance;
      ang = front.read();
      }   
  }
  front.write(ang);
Serial.print("the angle detected @ :- ");
  Serial.println(ang);
  
  }


void adjust()
{
  time = millis();
 speedl=50;
  speedr=46;
  digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  digitalWrite(brkf, HIGH);
  openwater();
  while ( (millis() - time)<1000 )
  {
if(pingchecknew() == 1 || irsens() == 1)
    {
     stopbot();
     closewater();
     
     return;
      }
 if(irsensl() == 1 )
    {
     digitalWrite(rmot, HIGH);
     digitalWrite(lmot, LOW);
     analogWrite(rpwm, 50);
     analogWrite(lpwm, 50);
     digitalWrite(brki, LOW);
     digitalWrite(brkj, LOW);
    delay(300);
    duration =duration +300;
     //Serial.println("left adjusted");
     digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
      }
      if(irsensr() == 1 )
    {
     digitalWrite(rmot, LOW);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, 50);
  analogWrite(lpwm, 50);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
  delay(300);
  duration =duration +300;
     //Serial.println("right adjusted");
     digitalWrite(rmot, HIGH);
  digitalWrite(lmot, HIGH);
  analogWrite(rpwm, speedr);
  analogWrite(lpwm, speedl);
  digitalWrite(brki, LOW);
  digitalWrite(brkj, LOW);
      }
    }

  stopbot();
  closewater();
  //Serial.println("Next command");  
  return;
    }
  
  
/*
__________________________________________________________________________________________________________________________________________________________________________________
 */ 
void loop() {
  //Serial.println("void loop started");
  if(pingcheck() ==1)
  {
     stopbot();
     Serial.println("danger");
    }
   
  flushinput();
  Serial.println("next command");
  while(Serial.available()==0){ //waiting here till the first command from laptop comes here
  }
  
  delay(55);//put python delay to 50
   str = Serial.readStringUntil('\n');
 //Serial.println(str);
 //Serial.println(str.charAt(0) );
 if (str.charAt(0) == 'f') 
   {
    Serial.println("foreward going");
    duration = str.substring(2).toInt();
    forward(duration); 
    
    } 
 else if (str.charAt(0) == 'b') 
   {
    duration = str.substring(2).toInt();
    backward(duration); 
    } 
 else if (str.charAt(0) =='l') 
   {
    pwm = str.substring(2).toInt();
    leftrotate( pwm);
    } 
else if (str.charAt(0) == 'r') 
   {
    pwm = str.substring(2).toInt();
    rightrotate( pwm);
    } 
else if (str.charAt(0) == 'c') 
   {
    Serial.println("Starting Cleaning ");
    cleanT();
    Serial.println("Completed Cleaning");
    } 
else if (str.charAt(0) == 'j')
  {
    duration = str.substring(2).toInt();
    forward(duration);
    delay(100);
    backward(duration); 
  }
else if (str.charAt(0) == 's')
  {
    delay(50);
    Serial.print(irsens() );
    Serial.print(" , ");
    Serial.println(pingcheck( )  );
   
  }
else if (str.charAt(0) == 'p')
  {
    Serial.println("Alligning perpendicularly");
    AllignP();
    Serial.println("Perpendicularly alligned");
  }
else if (str.charAt(0) == 'a')
  {
    backward(1000); 
   delay(100);
    int ang = random(30, 60);
    
     if (dir == 1){dir = 0 ;leftrotate( ang);leftrotate( ang);} 
     else if (dir == 0){dir = 1 ;rightrotate( ang);rightrotate( ang);} 
     
      } 
  
  

}
