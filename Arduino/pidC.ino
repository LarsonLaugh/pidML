#include <AverageThermocouple.h>
#include <MAX6675_Thermocouple.h>
#include <SmoothThermocouple.h>
#include <Thermocouple.h>

/*
    Name:       pidC.ino
    Created:  5/6/2022 8:36:44 AM
    Author:     LX
*/
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
# define DEFAULT_I2C_ADDR 0x27

# define SW 8
# define CLK 7
# define DT 6

# define SO 11
# define SCK 9
# define CS 10

# define SCL 5
# define SDA 4

# define RELAY 5 

LiquidCrystal_I2C lcd(DEFAULT_I2C_ADDR, 16, 2);
MAX6675_Thermocouple thermocouple(SCK,CS,SO);

int rot_add()
{
  int add = 0;
  bool flag_01 = false;
  bool flag_10 = false;
  while (digitalRead(CLK)==0 && digitalRead(DT)==1)
    flag_01 = true;
  while (digitalRead(CLK)==1 && digitalRead(DT)==0)
    flag_10 = true;
  if (flag_01)
    {
      if (digitalRead(CLK)==0 && digitalRead(DT)==0)
        add = 1;
      else if (digitalRead(CLK)==1 && digitalRead(DT)==1)
        add = -1;    
    }
   if (flag_10)
   {
      if (digitalRead(CLK)==1 && digitalRead(DT)==1)
        add = 1;
      else if (digitalRead(CLK)==0 && digitalRead(DT)==0)
        add = -1; 
   }
   return add;
}
    
void show_temp(LiquidCrystal_I2C lcd, float value, bool is_set_temp)
{
  if (is_set_temp)
  {
      lcd.setCursor(0,0);
      lcd.print("SET TEMP: ");
      lcd.setCursor(9,0);
      lcd.print(value);
      lcd.setCursor(14,0);
      lcd.print(" C");
  }
  else
  {
      lcd.setCursor(0,1);
      lcd.print("MES TEMP: ");
      lcd.setCursor(9,1);
      lcd.print(value);
      lcd.setCursor(14,1);
      lcd.print(" C");
  }
}

void showPID(LiquidCrystal_I2C lcd, int Kp, int Ki, int Kd, float output)
{
    lcd.setCursor(0,0);
    lcd.print("P:");
    lcd.setCursor(2,0);
    lcd.print(Kp);
    lcd.setCursor(6,0);
    lcd.print("I:");
    lcd.setCursor(8,0);
    lcd.print(Ki);
    lcd.setCursor(12,0);
    lcd.print("D:");
    lcd.print(Kd);
    lcd.setCursor(0,1);
    lcd.print("Output:");
    lcd.setCursor(8,1);
    lcd.print(output); 
}

void changePID(LiquidCrystal_I2C lcd, int Kp, int Ki, int Kd, int id_of_pid)
{
    lcd.setCursor(0,0);
    lcd.print("P:");
    lcd.setCursor(2,0);
    lcd.print(Kp);
    lcd.setCursor(6,0);
    lcd.print("I:");
    lcd.setCursor(8,0);
    lcd.print(Ki);
    lcd.setCursor(12,0);
    lcd.print("D:");
    lcd.print(Kd);
    lcd.setCursor(0,1);
    if (id_of_pid == 0)
      lcd.print("Setting P value");
    else if (id_of_pid == 1)
      lcd.print("Setting I value");
    else if (id_of_pid == 2)
      lcd.print("Setting D value");
}


void mode_switch_dial(LiquidCrystal_I2C lcd)
{
    lcd.setCursor(0,0);
    lcd.print("AutoPID-> Left");
    lcd.setCursor(0,1);
    lcd.print("ManPID-> Press");
}

int Kp = 88;
int Ki = 0;
int Kd = 18;
float set_temp = 30.0;
float read_temp = 0.0;
int screen_id = 0;
int num_of_screen = 6;
float output = 0;
float pid_tune_precision = 1.0;
float err = 0;
float inte = 0;
float deri = 0;
float lasterr = 0;
int datalog_flag = 0;

void setup()
{
    Serial.begin(9600);
    Serial.println("ready");

    lcd.begin();

    pinMode(SW, INPUT_PULLUP);
    pinMode(CLK, INPUT_PULLUP);
    pinMode(DT, INPUT_PULLUP);

    pinMode(RELAY, OUTPUT);


}

// Add the main program code into the continuous loop() function
void loop()
{
    if (digitalRead(SW)==0 || screen_id>=num_of_screen)
    {
      if (screen_id<num_of_screen)
        screen_id += 1;
      else
        screen_id = 0;
      lcd.clear();
    }
    switch (screen_id)
    {
      case 0:
      {
        show_temp(lcd,set_temp,true);
        show_temp(lcd,thermocouple.readCelsius(),false);
        break;
      }
      case 1:
      {
        showPID(lcd,Kp,Ki,Kd,output);
        if (rot_add()==-1)
          screen_id = 0;
        break;
      }
      case 2:
      {
        changePID(lcd,Kp,Ki,Kd,0);
        while (digitalRead(SW)== 1)
        {
          Kp += rot_add()*pid_tune_precision;
          changePID(lcd,Kp,Ki,Kd,0);
        }
        break;
      }
      case 3:
      {
        changePID(lcd,Kp,Ki,Kd,1);
        while (digitalRead(SW)== 1)
        {
          Ki += rot_add()*pid_tune_precision;
          changePID(lcd,Kp,Ki,Kd,1);
        }
        break;
      }
      case 4:
      {
        changePID(lcd,Kp,Ki,Kd,2);
        while (digitalRead(SW)== 1)
        {
          Kd += rot_add()*pid_tune_precision;
          changePID(lcd,Kp,Ki,Kd,2);
        }
        break;
      }
      case 5:
      {
        mode_switch_dial(lcd);
        if (rot_add() == -1)
        {
          Kp = 50;
          Ki = 50;
          Kd = 50;
          screen_id = 0;
        }
        break;
      } 
    }
  set_temp += rot_add();
  read_temp = thermocouple.readCelsius();
  err = set_temp - read_temp;
  inte += err;
  deri = (err-lasterr);
  lasterr = err;
  output = Kp*err + Ki*inte +Kd*deri;
  
  if (output<0)
    digitalWrite(RELAY,1);
  else
    digitalWrite(RELAY,0);
  Serial.println(output);
}
