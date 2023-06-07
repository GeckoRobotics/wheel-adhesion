import os
import pandas as pd
import matplotlib.pyplot as plt

dir = "/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/mvp_data/weld_data"
files = os.listdir(dir)
files.sort()

r = 0
c = 0
for file in files:

    # instantiate new figure when starting a new column
    if r == 0:
        plt.figure(f"C{c}", figsize=(20, 10))
    
    data = pd.read_csv(os.path.join(dir, file))

    # Extract magnetic field components
    Bx = data.loc[:, "Bx"]
    By = data.loc[:, "By"]
    Bz = data.loc[:, "Bz"]
    Bt = data.loc[:, "Btotal"] # total magnetic field  
    times = data.loc[:, "time"]

    seconds = [] # list of all times in seconds for current file
    for time in times:
        time = time[11:]
        time_list = time.split(":")
        hour = float(time_list[0])
        minute = float(time_list[1])
        second = float(time_list[2])
        total_seconds = 3600*hour + 60*minute + second
        seconds.append(total_seconds)

    # calculate time elapsed vector
    t = [0]
    for i in range(1, len(seconds)):
        delta_t = seconds[i] - seconds[i-1]
        t.append(t[i-1] + delta_t)

    # Plotting
    plt.subplot(3, 2, r+1)
    plt.plot(t, Bx, 'r')
    plt.plot(t, By, 'g')
    plt.plot(t, Bz, 'b')
    plt.plot(t, Bt, 'purple')
    plt.xlabel("Time (s)")
    plt.ylabel("Magnetic Field Strength (" + r'$\mu T$' + ")")
    plt.title(f"C{c}R{r}")

    r += 1

    # finish current column and prepare to start new one
    if r == 5:
        plt.figlegend(['Bx', 'By', 'Bz', 'Bt'])
        plt.subplots_adjust(hspace=0.4)
        plt.suptitle(f"C{c}") 
        plt.savefig(os.path.join(dir, f'C{c}')) # save figure to chosen directory
        r = 0 
        c += 1 
# display all figures created
plt.show()