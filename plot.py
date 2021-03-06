import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pidtrain import PID

plt.rc('lines', lw=1, color='k')  # thicker black lines
plt.rc('grid', c='0.5', ls='-', lw=0.5)  # solid gray grid lines
plt.rc('savefig', dpi=600)  # higher res outputs
plt.rc("font", size=20, family='arial', weight='light')
plt.rc("axes", labelsize=20, titlesize=20, linewidth=1)
plt.rc("xtick", direction='in', labelsize=20)
plt.rc('xtick.major', size=10, pad=7)
plt.rc('xtick.minor', size=5, pad=7, visible=True)
plt.rc("ytick", direction='in', labelsize=20)
plt.rc('ytick.major', size=10, pad=7)
plt.rc('ytick.minor', size=5, pad=7, visible=True)
plt.rc("legend", fontsize=20)
plt.rc('lines', linewidth=2)


def plot_compr():
    data = pd.read_csv('datalog.txt',
                       names=['time', 'temp', 'stemp', 'kp', 'ki', 'kd', 'error', 'integral', 'derivative', 'output'])
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(211)
    ax1 = fig.add_subplot(212)
    Time = np.linspace(0, 5 * len(data), len(data), dtype="int")
    ax.scatter(Time, data['temp'], color='b', label='Real',s=10)
    ax1.scatter(Time, data['output'], color='b', label='Real',s=10)

    setpoint = 56
    period = 0.001
    cycle_num = 7000

    # initialize PID controller
    pid = PID(88, 4.4, 18, setpoint, period)
    simu_temp, simu_output = pid.simulation(cycle_num)
    simu_time = np.linspace(0, cycle_num - 1, cycle_num, dtype="int")
    ax.plot(simu_time, simu_temp, color='r', label='Simulation')
    ax1.plot(simu_time, simu_output, color='r', label='Simulation')
    ax1.set_ylim(-2e4, 1e3)
    ax.set_ylabel('Temp (K)')
    ax.set_xlabel('Time (sec)')
    ax1.set_xlabel('Time (sec)')
    ax1.set_ylabel('output')
    ax.axhline(y=56, linewidth=2, linestyle='--')
    ax.legend(loc='best')
    ax1.legend(loc='best')
    # ax.set_xlim(1750,2000)
    # ax.set_ylim(50,60)
    ax.set_title("Real vs Simulation")
    plt.savefig('realvssimu')


def plot_gen(num1, num2, num3):
    dt = pd.read_csv("simu_setpt_65_genmax_100_popsz_20", index_col=False)
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    # pdata = dt[dt['Gen'] == num1].Kp.tolist()
    # idata = dt[dt['Gen'] == num1].Ki.tolist()
    # ddata = dt[dt['Gen'] == num1].Kd.tolist()
    pdata = dt['Kp'].tolist()
    idata = dt['Ki'].tolist()
    ddata = dt['Kd'].tolist()
    gdata = dt['Gen'].tolist()
    # ax.scatter(pdata, idata, ddata, color='b', label='gen1')
    ax.scatter(pdata, idata, ddata, c=gdata, cmap='coolwarm')

    # pdata = dt[dt['Gen'] == num2].Kp.tolist()
    # idata = dt[dt['Gen'] == num2].Ki.tolist()
    # ddata = dt[dt['Gen'] == num2].Kd.tolist()
    # ax.scatter(pdata, idata, ddata, color='y', label='gen50')
    #
    # pdata = dt[dt['Gen'] == num3].Kp.tolist()
    # idata = dt[dt['Gen'] == num3].Ki.tolist()
    # ddata = dt[dt['Gen'] == num3].Kd.tolist()
    # ax.scatter(pdata, idata, ddata, color='g', label='gen100')
    #
    # ax.legend(loc='best')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_zlim(0, 100)
    ax.set_xlabel('Kp')
    ax.set_ylabel('Ki')
    ax.set_zlabel('Kd')
    plt.show()


plot_compr()
