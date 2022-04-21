import pandas as pd
import matplotlib.pyplot as plt

dt = pd.read_csv("GeneticAlgorithm", index_col=False)
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
# pdata = dt[dt['Gen'] == 0].Kp.tolist()
# idata = dt[dt['Gen'] == 0].Ki.tolist()
# ddata = dt[dt['Gen'] == 0].Kd.tolist()
pdata = dt['Kp'].tolist()
idata = dt['Ki'].tolist()
ddata = dt['Kd'].tolist()
gdata = dt['Gen'].tolist()

ax.scatter(pdata, idata, ddata, c=gdata, cmap='coolwarm')
# pdata = dt[dt['Gen'] == 99].Kp.tolist()
# idata = dt[dt['Gen'] == 99].Ki.tolist()
# ddata = dt[dt['Gen'] == 99].Kd.tolist()
# ax.scatter(pdata, idata, ddata, color='r')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_zlim(0, 100)
ax.set_xlabel('Kp')
ax.set_ylabel('Ki')
ax.set_zlabel('Kd')
plt.show()
