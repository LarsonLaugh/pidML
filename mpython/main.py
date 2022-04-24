from machine import I2C, Pin
#import time
from time import sleep_ms, sleep_us, time_ns, time, localtime
from lcd1602_i2c import I2cLcd
from max6675 import MAX6675


# Define pins and address
DEFAULT_I2C_ADDR = 0x27
SWPIN, CLKPIN, DTPIN = 15, 6, 7
SOPIN, SCKPIN, CSPIN = 13, 12, 11
SCLPIN, SDAPIN = 5, 4
RELAYPIN = 17

# shortcut
i2c = I2C(0,scl=Pin(SCLPIN), sda=Pin(SDAPIN), freq=100000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

so = Pin(SOPIN, Pin.IN)
sck = Pin(SCKPIN, Pin.OUT)
cs = Pin(CSPIN, Pin.OUT)

SW = Pin(SWPIN, Pin.IN,Pin.PULL_UP) 
CLK = Pin(CLKPIN, Pin.IN,Pin.PULL_UP)
DT = Pin(DTPIN, Pin.IN,Pin.PULL_UP)
                                        
relay = Pin(RELAYPIN, Pin.OUT)


def readTemp(sck,cs,so):
    max = MAX6675(sck,cs,so)
    return max.read()

def rot_add(CLK,DT):
    
    add = 0
    flag_01, flag_10 = False, False
    while CLK.value()==0 and DT.value()==1:
        flag_01 = True
    while CLK.value()==1 and DT.value()==0:
        flag_10 = True
    if flag_01:
        if CLK.value() == 0 and DT.value() == 0:
            add = 1
        elif CLK.value() == 1 and DT.value() == 1:
            add = -1
    if flag_10:
        if CLK.value() == 1 and DT.value() == 1:
            add = 1
        elif CLK.value() == 0 and DT.value() == 0:
            add = -1
    return add

def show_temp(lcd,value,is_set_temp,lower_limit=0,upper_limit=100):
    
    if value > upper_limit:
        value = upper_limit
    if value < lower_limit:
        value = lower_limit
    if is_set_temp:
        lcd.move_to(0, 0)
        lcd.putstr("SET TEMP:")
        lcd.move_to(9, 0)
    else:
        lcd.move_to(0, 1)
        lcd.putstr("MES TEMP:")
        lcd.move_to(9, 1)
    lcd.putstr(' '+str(value)+'C')
    return value

def show_PID(lcd,Kp,Ki,Kd,output):
    
    lcd.move_to(0, 0)
    lcd.putstr('P:'+str(Kp)+' ')
    lcd.move_to(5, 0)
    lcd.putstr('I:'+str(Ki)+' ')
    lcd.move_to(10, 0)
    lcd.putstr('D:'+str(Kd)+' ')
    lcd.move_to(0, 1)
    lcd.putstr('Output:'+str(int(output)))

def datalog(f,data):
    
    f.write(str(localtime()[3])+':'+str(localtime()[4])+':'+str(localtime()[5])+',') # time
    f.write(str(data['read_temp'])+','+str(data['set_temp'])+',') # temp
    f.write(str(data['Kp'])+','+str(data['Ki'])+','+str(data['Kd'])+',') # PID parameters
    f.write(str(data['err'])+','+str(data['inte'])+','+str(data['deri'])+','+str(data['output'])) # PID parameters
    f.write('\n')
    print(localtime()[3],localtime()[4],localtime()[5])
    
    
# PID parameters
Kp, Ki, Kd = 88, 4.4, 18

# predefine
set_temp, read_temp = 30, 0
time_interval = 1 # in unit of second
last_update = time()
err, inte, deri, output, lasterr = 0, 0, 0, 0, 0 # initialize PID parameters
toggle_pid = False # toggle display
datalog_flag = 0
# create a datalog file
f = open("datalog.txt","a")
f.write("Data Logger \n")
f.write("Time, TempRead, TempSet, Kp, Ki, Kd, error, integral, derivate, output\n")
f.close()

# loop
while True:
# display   
    if SW.value() == 0:
        toggle_pid = not toggle_pid
        sleep_ms(1000)
        lcd.clear()
    if toggle_pid:
        show_PID(lcd,Kp,Ki,Kd,output)
    else:
        set_temp = show_temp(lcd,set_temp,is_set_temp=True)
        show_temp(lcd,read_temp,is_set_temp=False)
# turn set temperature        
    set_temp+=rot_add(CLK,DT)
    
    now = time()
    dt = now-last_update   
# update after a period of time
    if dt>time_interval-1:
        datalog_flag+=1
        
        read_temp = float(readTemp(sck,cs,so))
        
        # update PID inputs and calculate output    
        err =  set_temp-read_temp
        inte = inte + err*dt
        deri = (err-lasterr)/dt
        lasterr = err
        output = Kp*err+Ki*inte+Kd*deri
        last_update = now
        
        if datalog_flag>4:
            data = {}
            data['read_temp'], data['set_temp'] = read_temp, set_temp
            data['Kp'], data['Ki'], data['Kd'] = Kp, Ki, Kd
            data['err'], data['inte'], data['deri'], data['output'] = err, inte, deri, output
            
            with open("datalog.txt","a") as f:
                datalog(f,data)
                
            datalog_flag = 0

    if output<0: 
        relay.value(1) # switch off the heater circuit
    else:    # if output>=0, switch on the heater circuit
        relay.value(0)
    sleep_ms(1)    
            
                