import matplotlib.pyplot as plt
import numpy as np

x = np.arange(-np.pi,np.pi,0.01)
y = np.sin(x)
plt.plot(x,y,'ro')
plt.savefig("File/chart1.png",dpi=75)
plt.show()

