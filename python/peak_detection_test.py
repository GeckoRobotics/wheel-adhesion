from peak_detection_algorithm import thresholding_algo
import numpy as np
import pylab
import os
import pandas as pd

dir = "/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/raw/differential/large_weld_line"
files = os.listdir(dir)
data = pd.read_csv(os.path.join(dir, files[0]))

y = data.loc[:, "Bt-top"]
y = y.to_numpy()

# adjustable parameters
lag = 5
threshold = 2.9
influence = 0.6

# Run algo with settings from above
result = thresholding_algo(y, lag=lag, threshold=threshold, influence=influence)
lower_bound = result["avgFilter"] - (threshold * result["stdFilter"])
upper_bound = result["avgFilter"] + (threshold * result["stdFilter"])


# Plot result
pylab.subplot(211)
pylab.plot(np.arange(1, len(y)+1), y)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"], color="cyan", lw=2)

pylab.plot(np.arange(1, len(y)+1),
           upper_bound, color="green", lw=2)

pylab.plot(np.arange(1, len(y)+1),
           lower_bound, color="orange", lw=2)

pylab.subplot(212)
pylab.step(np.arange(1, len(y)+1), result["signals"], color="red", lw=2)
pylab.ylim(-1.5, 1.5)
pylab.show()





