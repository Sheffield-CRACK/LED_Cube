'''Handler to light up the LEDs.

Anode rails must be on
'''

import gpiozero
import time

def flash_LED(x, y, pulse_length=10):
    '''Flash an LED at coordinate x, y for z ms
    
    Inputs:
    -------
    x, int:
        The x pin, which will have a HI voltage applied
    y, int:
        The y pin, which will have a LO voltage applied
    pulse_length, float:
        The length of the pulse in milliseconds
    '''
    print("flashing {}, {}".format(x, y))
    time.sleep(pulse_length/1000.)

def flash_grid(grid, pulse_length=10):
    '''Flash a whole grid. Takes a 2D numpy array and passes it through'''
    pulse_length = pulse_length * 1e-3

    for i, layer in enumerate(grid):
        # APPLY VOLTAGE TO CATHODE PIN, <i>
        print("Applying GND to pin {}".format(i))
        for j, is_on in enumerate(layer):
            if is_on:
                # APPLY VOLTAGE TO ANODE PIN, <j>
                print("Apply +V to pin {}".format(j))
            time.sleep(pulse_length)