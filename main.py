from time import time, sleep


class PID():
    def __init__(self, kp, ki, kd, setpoint, period, cycle_num):
        self.temp = 0
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.period = period
        self.integral = 0
        self.last_error = 0
        self.start_time = time()
        self.cycle_num = cycle_num
        self.curr_cycle = 1

    def get_integral(self):
        return self.integral

    def set_integral(self, value):
        self.integral = value

    def get_last_error(self):
        return self.last_error

    def set_last_error(self, value):
        self.last_error = value

    def get_start_time(self):
        return self.start_time

    def get_setpoint(self):
        return self.setpoint

    def get_period(self):
        return self.period

    def get_pid(self):
        return self.kp, self.ki, self.kd

    def set_temp(self, value):
        self.temp = value

    def get_temp(self):
        return self.temp

    def set_curr_cycle(self, value):
        self.curr_cycle = value

    def get_curr_cycle(self):
        return self.curr_cycle

    def get_cycle_num(self):
        return self.cycle_num

    def output(self, temp):
        error = self.get_setpoint() - temp
        integral = self.get_integral() + error
        derivative = (error - self.get_last_error()) / self.get_period()
        kp, ki, kd = self.get_pid()
        return kp * error + ki * integral + kd * derivative


# initialize PID controller
kp, ki, kd = 1, 1, 10
setpoint = 3
cycle_num = 100
period = 1
pidtest = PID(kp, ki, kd, setpoint, period, cycle_num)
# while loop
while pidtest.get_cycle_num() > pidtest.get_curr_cycle():
    output = pidtest.output(pidtest.get_temp())
    if output > 0:
        pidtest.set_temp(pidtest.get_temp() + 1)
    else:
        pidtest.set_temp(pidtest.get_temp() - 0.1)
    print(pidtest.get_curr_cycle(), pidtest.get_temp())
    sleep(pidtest.get_period())
    pidtest.set_curr_cycle(pidtest.get_curr_cycle()+1)
