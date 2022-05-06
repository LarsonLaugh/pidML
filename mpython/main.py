from machine import I2C, Pin
from time import time, localtime
from lcd1602_i2c import I2cLcd
from max6675 import MAX6675

# Define pins and address
DEFAULT_I2C_ADDR = 0x27
SWPIN, CLKPIN, DTPIN = 15, 6, 7
SOPIN, SCKPIN, CSPIN = 13, 12, 11
SCLPIN, SDAPIN = 5, 4
RELAYPIN = 17

# shortcut
i2c = I2C(0, scl=Pin(SCLPIN), sda=Pin(SDAPIN), freq=100000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

so = Pin(SOPIN, Pin.IN)
sck = Pin(SCKPIN, Pin.OUT)
cs = Pin(CSPIN, Pin.OUT)

SW = Pin(SWPIN, Pin.IN, Pin.PULL_UP)
CLK = Pin(CLKPIN, Pin.IN, Pin.PULL_UP)
DT = Pin(DTPIN, Pin.IN, Pin.PULL_UP)

relay = Pin(RELAYPIN, Pin.OUT)


def readTemp(sck, cs, so):
    max = MAX6675(sck, cs, so)
    return max.read()


def rot_add(CLK, DT):  # detect lEFT (-1) or RIGHT (+1) rotation

    add = 0
    flag_01, flag_10 = False, False
    while CLK.value() == 0 and DT.value() == 1:
        flag_01 = True
    while CLK.value() == 1 and DT.value() == 0:
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


def show_temp(lcd, value, is_set_temp):  # screen 0

    if is_set_temp:
        lcd.move_to(0, 0)
        lcd.putstr("SET TEMP:")
        lcd.move_to(9, 0)
    else:
        lcd.move_to(0, 1)
        lcd.putstr("MES TEMP:")
        lcd.move_to(9, 1)
    lcd.putstr(' ' + "{:.2f}".format(value) + 'C')
    return value


def show_PID(lcd, Kp, Ki, Kd, output):  # screen 1

    lcd.move_to(0, 0)
    lcd.putstr('P:' + str(Kp) + ' ')
    lcd.move_to(6, 0)
    lcd.putstr('I:' + str(Ki) + ' ')
    lcd.move_to(12, 0)
    lcd.putstr('D:' + str(Kd) + ' ')
    lcd.move_to(0, 1)
    lcd.putstr('Output:' + str(int(output)))


def change_PID(lcd, Kp, Ki, Kd, id_of_pid):  # screen 2, 3, 4
    lcd.move_to(0, 0)
    lcd.putstr('P:' + str(Kp) + ' ')
    lcd.move_to(6, 0)
    lcd.putstr('I:' + str(Ki) + ' ')
    lcd.move_to(12, 0)
    lcd.putstr('D:' + str(Kd) + ' ')
    lcd.move_to(0, 1)
    if id_of_pid == 0:
        lcd.putstr('Setting P value')
    elif id_of_pid == 1:
        lcd.putstr('Setting I value')
    elif id_of_pid == 2:
        lcd.putstr('Setting D value')
    else:
        print('id_of_pid must be 0, 1, 2 for P, I, D')


def mode_switch_dial(lcd):  # screen 5
    lcd.move_to(0, 0)
    lcd.putstr('AutoPID -> left')
    lcd.move_to(0, 1)
    lcd.putstr('ManPID-> press')


def datalog(f, data):
    f.write(str(localtime()[3]) + ':' + str(localtime()[4]) + ':' + str(localtime()[5]) + ',')  # time
    f.write(str(data['read_temp']) + ',' + str(data['set_temp']) + ',')  # temp
    f.write(str(data['Kp']) + ',' + str(data['Ki']) + ',' + str(data['Kd']) + ',')  # PID parameters
    f.write(str(data['err']) + ',' + str(data['inte']) + ',' + str(data['deri']) + ',' + str(
        data['output']))  # PID parameters
    f.write('\n')


#     print(localtime()[3],localtime()[4],localtime()[5])


# PID parameters
Kp, Ki, Kd = 88, 0, 18
Kp_default, Ki_default, Kd_default = 50, 50, 50
# predefine
set_temp, read_temp = 30, 0
time_interval = 1  # in unit of second
last_update = time()
err, inte, deri, output, lasterr = 0, 0, 0, 0, 0  # initialize PID parameters
toggle_pid = False  # toggle display
datalog_flag = 0
# UI setting
screen_id = 0 # default main screen 0
num_of_screen = 6
# create a datalog file
f = open("datalog.txt", "a")
f.write("Data Logger \n")
f.write("Time, TempRead, TempSet, Kp, Ki, Kd, error, integral, derivate, output\n")
f.close()
pid_tune_precision = 1
# loop
while True:
    # user interface (UI)
    if SW.value() == 0 or screen_id >= num_of_screen:
        if screen_id < num_of_screen:
            screen_id += 1
        else:
            screen_id = 0
        lcd.clear()
    if screen_id == 0:
        show_temp(lcd, set_temp, is_set_temp=True)
        show_temp(lcd, read_temp, is_set_temp=False)
    #         print('**', set_temp, ' ',read_temp, '**')
    elif screen_id == 1:
        show_PID(lcd, Kp, Ki, Kd, output)
        if rot_add(CLK, DT) == -1:  # left turn to return home screen
            screen_id = 0
    elif screen_id == 2:
        change_PID(lcd, Kp, Ki, Kd, 0)
        while SW.value() == 1:
            Kp += rot_add(CLK, DT) * pid_tune_precision
            change_PID(lcd, Kp, Ki, Kd, 0)
    elif screen_id == 3:
        change_PID(lcd, Kp, Ki, Kd, 1)
        while SW.value() == 1:
            Ki += rot_add(CLK, DT) * pid_tune_precision
            change_PID(lcd, Kp, Ki, Kd, 1)
    elif screen_id == 4:
        change_PID(lcd, Kp, Ki, Kd, 2)
        while SW.value() == 1:
            Kd += rot_add(CLK, DT) * pid_tune_precision
            change_PID(lcd, Kp, Ki, Kd, 2)
    elif screen_id == 5:
        mode_switch_dial(lcd)
        if rot_add(CLK, DT) == -1:  # left turn to use Auto mode
            Kp, Ki, Kd = Kp_default, Ki_default, Kd_default
            screen_id = 0
    print(Kp)
    print('\n*')
    # set temperature
    set_temp += rot_add(CLK, DT)

    now = time()
    dt = now - last_update
    # update after a period of time
    if dt > time_interval - 1:
        datalog_flag += 1

        read_temp = float(readTemp(sck, cs, so))

        # update PID inputs and calculate output
        err = set_temp - read_temp
        inte = inte + err * dt
        deri = (err - lasterr) / dt
        lasterr = err
        output = Kp * err + Ki * inte + Kd * deri
        last_update = now

        if datalog_flag > 4:
            data = {}
            data['read_temp'], data['set_temp'] = read_temp, set_temp
            data['Kp'], data['Ki'], data['Kd'] = Kp, Ki, Kd
            data['err'], data['inte'], data['deri'], data['output'] = err, inte, deri, output

            with open("datalog.txt", "a") as f:
                datalog(f, data)

            datalog_flag = 0

    if output < 0:
        relay.value(1)  # switch off the heater circuit
    else:  # if output>=0, switch on the heater circuit
        relay.value(0)


