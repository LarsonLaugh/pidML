import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from main import PID

data = pd.read_csv('datalog.txt',
                   names=['time', 'temp', 'stemp', 'kp', 'ki', 'kd', 'error', 'integral', 'derivative', 'output'])

fig = plt.figure()
ax = fig.add_subplot(111)
ax1 = ax.twinx()
Time = np.linspace(0, 5 * len(data), len(data), dtype="int")
ax.plot(Time, data['temp'], color='b')
ax1.plot(Time, data['output'], color='g')

setpoint = 56
period = 0.001
cycle_num = 7000

# initialize PID controller
pid = PID(88, 4.4, 18, setpoint, period)
simu_temp, simu_output = pid.simulation(cycle_num)
simu_time = np.linspace(0, cycle_num - 1, cycle_num, dtype="int")
ax.plot(simu_time, simu_temp, color='r')
ax1.plot(simu_time, simu_output, color='k')
ax1.set_ylim(-2e4, 1e3)

# dt = pd.read_csv("GeneticAlgorithm", index_col=False)
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# pdata = dt[dt['Gen'] == 0].Kp.tolist()
# idata = dt[dt['Gen'] == 0].Ki.tolist()
# ddata = dt[dt['Gen'] == 0].Kd.tolist()
# # pdata = dt['Kp'].tolist()
# # idata = dt['Ki'].tolist()
# # ddata = dt['Kd'].tolist()
# # gdata = dt['Gen'].tolist()
# ax.scatter(pdata, idata, ddata, color='b',label='gen1')
# # ax.scatter(pdata, idata, ddata, c=gdata, cmap='coolwarm')
#
# pdata = dt[dt['Gen'] == 9].Kp.tolist()
# idata = dt[dt['Gen'] == 9].Ki.tolist()
# ddata = dt[dt['Gen'] == 9].Kd.tolist()
# ax.scatter(pdata, idata, ddata, color='y',label='gen10')
#
# pdata = dt[dt['Gen'] == 19].Kp.tolist()
# idata = dt[dt['Gen'] == 19].Ki.tolist()
# ddata = dt[dt['Gen'] == 19].Kd.tolist()
# ax.scatter(pdata, idata, ddata, color='g',label='gen20')
#
# ax.legend(loc='best')
#
#
# ax.set_xlim(0, 100)
# ax.set_ylim(0, 100)
# ax.set_zlim(0, 100)
# ax.set_xlabel('Kp')
# ax.set_ylabel('Ki')
# ax.set_zlabel('Kd')
plt.show()
