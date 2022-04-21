import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import time, sleep
from numpy.random import rand, random_sample
from mpl_toolkits import mplot3d

class PID():
    def __init__(self, kp, ki, kd, setpoint, period):
        self.temp = 0
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.period = period
        self.integral = 0
        self.last_error = 0
        self.start_time = time()
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

    def output(self, temp):
        error = self.get_setpoint() - temp
        integral = self.get_integral() + error
        derivative = (error - self.get_last_error()) / self.get_period()
        kp, ki, kd = self.get_pid()
        self.set_integral(integral)
        self.set_last_error(error)
        return kp * error + ki * integral + kd * derivative

    def simulation(self, cycle_num):
        temp_logger = []
        self.set_curr_cycle(1)
        while cycle_num + 1 > self.get_curr_cycle():
            temp_curr = self.get_temp()
            temp_logger.append(temp_curr)
            output = self.output(temp_curr)
            if output > 0:
                self.set_temp(temp_curr + 0.5)
            else:
                self.set_temp(temp_curr - 0.1)
            # print(self.get_curr_cycle(), self.get_temp())
            sleep(self.get_period())
            self.set_curr_cycle(self.get_curr_cycle() + 1)
        return temp_logger

    @staticmethod
    def mae_cost(data, setpoint):
        n = len(data)
        return sum([abs(dt - setpoint) for dt in data]) / n

    @staticmethod
    def mse_cost(data, setpoint):
        n = len(data)
        return sum([(dt - setpoint)**2 for dt in data]) / n

def pid_hybrid(pid1,pid2):
    dice = rand()*3
    if 0 <= dice < 1:
        pid1_new = np.array([pid2[0],pid1[1],pid1[2]])
        pid2_new = np.array([pid1[0],pid2[1],pid2[2]])
    elif 1 <= dice < 2:
        pid1_new = np.array([pid1[0],pid2[1],pid1[2]])
        pid2_new = np.array([pid2[0],pid1[1],pid2[2]])
    else:
        pid1_new = np.array([pid1[0],pid1[1],pid2[2]])
        pid2_new = np.array([pid2[0],pid2[1],pid1[2]])
    return pid1_new, pid2_new

def pid_mutation():
    return 100*random_sample(3)

def elitism(K,Cost):
    return K[Cost.index(min(Cost))]

if __name__ == "__main__":
    setpoint = 3.5
    period = 0.01
    GenMax = 20
    PopSize= 10
    cycle_num = 100

    # initialize PID controller
    pid_data = pd.DataFrame()
    for gen in range(GenMax):
        print('generation # ', gen)
    # First generation
        if gen == 0:
            K = 100*random_sample((PopSize,3))
        Cost = []
        for i in range(PopSize):
            pid = PID(K[i][0], K[i][1], K[i][2], setpoint, period)
            cost = pid.mae_cost(pid.simulation(cycle_num),setpoint)
            Cost.append(cost)
            print(K[i][0], K[i][1], K[i][2],cost)
            pid_data = pid_data.append({'Kp': K[i][0], 'Ki': K[i][1], 'Kd': K[i][2], 'Cost': cost, 'Gen': gen},ignore_index=True)
    # Genetic algorithm
        K_prime = K
        # Elitism
        K_prime[0] = elitism(K,Cost)
        # hybrization
        for j in [1,3,5,7]:
            K_prime[j], K_prime[j+1] = pid_hybrid(K[j], K[j+1])
        # mutation
        K_prime[PopSize-1] = pid_mutation()
        K = K_prime


    # plot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    pdata = pid_data['Kp'].tolist()
    idata = pid_data['Ki'].tolist()
    ddata = pid_data['Kd'].tolist()
    gdata = pid_data['Gen'].tolist()
    ax.scatter(pdata,idata,ddata,c = gdata, cmap = 'coolwarm')
    ax.set_xlim(0,100)
    ax.set_ylim(0,100)
    ax.set_zlim(0,100)
    ax.set_xlabel('Kp')
    ax.set_ylabel('Ki')
    ax.set_zlabel('Kd')
    plt.show()
    pid_data.to_csv("GeneticAlgorithm")
