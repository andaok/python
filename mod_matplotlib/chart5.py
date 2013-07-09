# -*- encoding:utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import array

x = np.array([100,300,500,700,900,1100,1300,1500,1700,1900,2100,2300,2500,2700,2900,3100,5000,6000,7000,8000,9000])
v1 = np.array([91064.73,112160.44,99575.8,85041.25,82049.27,75707.11,84415.26,84435.21,86810.08,79677.47,79662.23,80539.94,78405.55,79813.55,76635.41,71697.95,64941.82,69928.12,70387.84,70044.69,73825.81])
v2 = np.array([54.91,44.58,50.21,58.79,60.94,66.04,59.23,59.22,57.61,62.75,62.76,62.08,63.77,62.65,65.24,69.74,76.99,71.51,71.04,71.38,67.73])


plt.plot(x,v1,'bo-',label="Redis Get")
plt.ylabel("QPS")
plt.xlabel("Concurrent Number")
plt.grid(True)
plt.legend(loc='1')

a = plt.axes([.50, .5 , .3 ,.3], frameon = True,xticks=[100,9000])
rect = plt.plot(x,v2,'bo-')
plt.xlabel("Concurrent Number")
plt.ylabel("Elapsed Time")
plt.grid(True)


plt.savefig("File/chart5.png",dpi=75)
plt.show()

