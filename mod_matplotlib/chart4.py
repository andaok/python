# -*- encoding:utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import array

x = np.array([100,300,500,700,900,1100,1300,1500,1700,1900,2100,2300,2500,2700,2900,3100,5000,6000,7000,8000])
v1 = np.array([96011.67,82609.12,75431.84,70707.36,71116.67,66424.88,65974.38,67154.66,66755.67,63181.57,67642.52,62684.92,59915.41,53795.83,50845.56,50872.98,51583.62,54626.31,53724.73,31154.78])
v2 = np.array([52.08,60.53,66.29,70.71,70.31,75.27,75.79,74.46,74.91,79.14,73.92,79.76,83.45,92.94,98.34,98.28,96.93,91.53,93.07,160.49])


plt.plot(x,v1,'bo-')
plt.ylabel("QPS")
plt.xlabel("Concurrent Number")
plt.grid(True)

a = plt.axes([.50, .5 , .3 ,.3], frameon = True,xticks=[100,8000])
plt.plot(x,v2,'bo-')
plt.xlabel("Concurrent Number")
plt.ylabel("Elapsed Time")
plt.grid(True)

plt.savefig("File/chart4.png",dpi=75)
plt.show()

