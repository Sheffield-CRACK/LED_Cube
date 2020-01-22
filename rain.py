from send_cube import connect_cube, send_cube
import numpy as np

from pprint import pprint
from time import sleep

N_LAYERS = 8
N_REGISTERS = 8
N_BITS = 8

DROP_RATE = 1 - 0.75       # 1/average drops per layer
RAIN_FALL_RATE = 1.0  # seconds on screen per drop

delay = RAIN_FALL_RATE / N_LAYERS

try:
    arduino = connect_cube()
except Exception as e:
    print(repr(e))
    arduino = None

# List of my raindrops. (x, y)
drops = []
MEAN_N = []
while True:
    grid = np.zeros((N_LAYERS, N_REGISTERS, N_BITS))

    new_drops = []
    for drop in drops:
        layer, reg, bit = drop
        layer += 1
        if layer < N_LAYERS:
            new_drops.append((layer, reg, bit))

    # Randomly add new drops
    while np.random.rand() > DROP_RATE:
        reg = np.random.randint(0, N_REGISTERS)
        bit = np.random.randint(0, N_BITS)

        new_drop = (0, reg, bit)
        new_drops.append(new_drop)
    drops = new_drops

    for drop in drops:
        grid[drop] = 1

    if arduino is not None:
        send_cube(arduino, grid)

    N = np.zeros(N_LAYERS)
    for drop in drops:
        N[drop[0]] += 1
    MEAN_N.append(np.mean(N))
    print("Mean drops per layer: {:.2f}".format(np.mean(MEAN_N)), end='\r')

    sleep(delay)