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
    Bt = data.loc[:, "Btotal"] # total magnetic field        plt.figsize(20, 10)
    time_idx = 11 # start index of time in date+time string in DataFrame
    t = list(range(0, len(Bx))) # time indices

    # Plotting
    plt.subplot(3, 2, r+1)
    plt.plot(t, Bx, 'r')
    plt.plot(t, By, 'g')
    plt.plot(t, Bz, 'b')
    plt.plot(t, Bt, 'purple')
    plt.ylabel("Magnetic Field Strength (" + r'$\mu T$' + ")")
    plt.title(f"C{c}R{r}")

    r += 1

    # finish current column and prepare to start new one
    if r == 5:
        plt.figlegend(['Bx', 'By', 'Bz', 'Bt'])
        plt.suptitle(f"C{c}") 
        plt.savefig(os.path.join(dir, f'C{c}'))
        r = 0 
        c += 1 

# display all figures created
plt.show()