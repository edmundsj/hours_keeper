# file to generate cool plots

import matplotlib.pyplot as plt
from data_classes import *
import numpy as np
from appJar import gui


data = TimeData("time_data_all.csv")
matrix_data = data.generate_hourly_data(datetime.datetime(2018, 4, 1), datetime.datetime(2018, 4, 7))

plt.imshow(matrix_data, cmap=plt.cm.RdYlGn)
plt.axis([0, 23, 0, 8])
plt.xticks(np.arange(0, 24, 1))
plt.yticks(np.arange(0, 9, 1))
plt.colorbar()

plt.ion()
plt.show()
plt.pause(0.01)
yesno = ""
while(yesno != "q"):
	yesno = input("Would you like to see another plot? ")
