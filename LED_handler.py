'''Handler to light up the LEDs.

Anode rails must be on
'''

import threading
import time

import gpiozero
import numpy as np


class LEDHandler(object):
    '''Control the GPIO Pins to operate the LED cube.'''
    def __init__(self, grid, pulse_duration=5e-3, duty_cycle=0.5, debug=False):
        self.debug = debug
        self.grid = grid

        if self.debug:
            print("Grid initialised to:")
            print(self.grid)

        # TODO:
        # Should this be a grid flash frequency, rather than a pulse duration?
        self.pulse_duration = pulse_duration
        self.duty_cycle = duty_cycle

        # The cathodes are assumed to be the first dimension.
        # These will control transistors that let the current flow through
        # a specific layer.
        # Pins 0 and 1 are reserved. Don't use them.
        self.anodes = [gpiozero.DigitalOutputDevice(
            pin=i, active_high=True, initial_value=False)
            for i in range(2, self.X+2)
        ]

        # There will be Y*Z anodes.
        # They will control whether an index is on or off.
        start = self.X + 2
        stop = start + (self.Y * self.Z)
        self.cathodes = [gpiozero.DigitalOutputDevice(
            pin=j, active_high=True, initial_value=False)
            for j in range(start, stop)
        ]

        # Start a thread that literally just calls the flash_grid method
        # over and over, ad infinitum.
        self.is_on = False
        self.thread = threading.Thread(target=self.__run__)

    def __run__(self):
        while True:
            sleep = (1.0-self.duty_cycle) / self.pulse_frequency
            time.sleep(sleep)
            self.flash_grid()

    @property
    def is_on(self):
        return self.__is_on
    @is_on.setter
    def is_on(self, is_on):
        self.__is_on = is_on

    @property
    def grid(self):
        return self.__grid
    @grid.setter
    def grid(self, grid):
        self.__grid = grid

        # Save the dimensions
        self.X, self.Y, self.Z = grid.shape

    @property
    def pulse_frequency(self):
        n_flashes = float(self.X + (self.Y * self.Z))
        time_per_flash = self.pulse_duration * n_flashes

        return 1./time_per_flash

    def flash_grid(self):
        '''If I'm on, flash the grid. Otherwise, just do nothing. '''
        if self.is_on:
            for cathode, layer in zip(self.cathodes, self.grid):
                if self.debug:
                    print("Activating {}".format(cathode.pin))
                cathode.on()

                # Get the layer in 1D - the LEDs are hooked up in only 2D,
                # but arranged in 3D!
                layer = layer.flatten()

                # Activate the pins we want
                for anode, is_on in zip(self.anodes, layer):
                    if is_on:
                        if self.debug:
                            print("Activating pin {}".format(anode.pin))
                        anode.on()

                # Leave them on for long enough to see
                time.sleep(self.pulse_duration)
                if self.debug:
                    print("Resetting all pins")
                for anode in self.anodes:
                    anode.off()
                cathode.off()

        # If I'm not on, cycle through just the same, but without toggling the
        # pins
        else:
            if self.debug:
                print("LED grid not active")
            for cathode in self.cathodes:
                for anode in self.anodes:
                    time.sleep(self.pulse_duration)


    def flash_LED(self, x, y, z, pulse_duration=1):
        '''Flash the LED at coordinate (x, y, z)'''
        # LAYER 1
        # [[[1, 0, 1],
        #   [0, 0, 0],
        #   [1, 0, 1]],

        # LAYER 2
        #  [[0, 0, 0],
        #   [0, 1, 0],
        #   [0, 0, 0]],

        # LAYER 3
        #  [[1, 0, 1],
        #   [0, 0, 0],
        #   [1, 0, 1]]]

        # The anode we want is easy - just the layer.
        self.anodes[x].on()

        # The relevant cathode is less trivial
        index = 2 + (y * self.Z) + z

        print("Flashing cathode GPIO{:02d}".format(index))
        self.cathodes[index].on()

        time.sleep(pulse_duration)

        # Turn off the pins again
        self.anodes[x].off()
        self.cathodes[index].off()

    def close(self):
        '''Gracefully shutdown the pins'''
        for anode in self.anodes:
            anode.close()
        for cathode in self.cathodes:
            cathode.close()