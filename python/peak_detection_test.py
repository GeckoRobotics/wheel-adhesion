from peak_detection_algorithm import thresholding_algo
import numpy as np
import pylab


y = np.array([1218.29, 1219.49, 1215.46, 1218.59, 1221.59, 1228.22, 1230.85, 1230.74, 1226.36, 1240.37, 1267.84, 1263.84, 1259.17, 1255.95, 1252.94, 1253.83, 1256.55, 1253.39, 1258.68, 1258.14, 1266.45, 1259.24, 1261.87, 1257.11, 1251.25, 1248.3, 1252.36, 1216.69, 1218.53, 1220.81, 1223.87, 1221.87, 1219.02, 1222.47, 1223.8, 1221.03, 1220.68, 1214.76, 1215.24, 1217.75, 1213.96, 1210.61, 1217.42])

lag = 3
threshold = 7
influence = 0.7

# Run algo with settings from above
result = thresholding_algo(y, lag=lag, threshold=threshold, influence=influence)

# Plot result
pylab.subplot(211)
pylab.plot(np.arange(1, len(y)+1), y)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"], color="cyan", lw=2)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"] + threshold * result["stdFilter"], color="green", lw=2)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"] - threshold * result["stdFilter"], color="orange", lw=2)

pylab.subplot(212)
pylab.step(np.arange(1, len(y)+1), result["signals"], color="red", lw=2)
pylab.ylim(-1.5, 1.5)
pylab.show()



