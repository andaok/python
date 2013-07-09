# -*- encoding:utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import array

x = np.arange(0,11,1)
v1 = np.array([1,3,5,5,6,7,5,5,5,3,2])
v2 = np.array([52.08,60.53,66.29,70.71,70.31,75.27,75.79,74.46,74.91,79.14,73.92,79.76,83.45,92.94,98.34,98.28])

plt.axis([0,11,-100,100])
plt.figure(1)
#plt.subplot(211)

plt.plot(x,v1,'bo-')
plt.ylabel("QPS")
plt.xlabel("Concurrent Number")
plt.grid(True)


"""
plt.subplot(212)
plt.plot(x,v2,'bo-')
plt.xlabel("Concurrent Number")
plt.ylabel("Elapsed Time")
plt.grid(True)
"""

plt.savefig("File/chart6.png",dpi=75)
plt.show()

