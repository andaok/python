import matplotlib.pyplot as plt
import numpy as np

x = np.arange(-5,5,0.01)
y = x**3
plt.axis([-6,6,-10,10])
plt.plot(x,y)
plt.grid(True)
plt.savefig("File/chart2.png",dpi=75)
plt.show()

