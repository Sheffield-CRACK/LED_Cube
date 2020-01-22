'''James Wild, Jan. 2020.

LED cube matrix python handler. The Arduino does the boring grunt work of
sorting the cube out, so that you can generate cool stuff here without worrying
too much about nonsense.

As far as I've tested so far, the transmit time is pretty negligible (I think
on the order 1ms, but fuck knows), so if you want people to see whatever you're
throwing up there you will likely have to add in delays.

Most of this is stuff YOU don't need to care about. For the end-user, it is simple:
    arduino = connect_cube() # Searches ports for a connected arduino

    data = np.ones((8,8,8))  # Fully illuminates the cube
    send_cube(arduino, data) # Send the data

    data = np.zeros((8,8,8)) # Turns the cube off
    send_cube(arduino, data) # Send the data

    arduino.close()          # Close the connection to the arduino.
'''

import serial
import numpy as np
import time
import serial.tools.list_ports

N_REGISTERS = 8 # How many registers are daisy-chained?
N_BITS      = 8 # How many bits does each SR handle? (usulaly 8)
N_LAYERS    = 8 # How many layers do we have?

BAUDRATE = 9600


def conv2byte(byte):
    '''Convert iterable data to a byte. This can be presented three ways:
      - int, either 0 or any number >0
      - bool
      - str, the string 1 vs any other string (including an empty one)

    The iterable must be exactly 8 items long. So, the follwoing will all will give the same result:
      - "00110101"
      - ['0','0','1','1','0','1','0','1']
      - [0, 0, 1, 1, 0, 1, 0, 1]
      - [False, False, True, True, False, True, False, True]

    Returns the integer form of that byte.'''

    assert len(byte) == 8, "Byte must be 8 items long, got {}".format(len(byte))

    if type(byte[0]) != str:
        byte = ['1' if bit else '0' for bit in byte]

    byte = ''.join(byte)
    out = int(byte, base=2)

    return out


def conv2byte_vect(cube):
    '''Convert a cube to bytes. The cube provided will be converted to a numpy array

    !!! BE AWARE!!!
    To write to the LED cube, it should be in the shape (N_LAYERS, N_REGISTERS, N_BITS)'''
    new_cube = []
    cube = np.array(cube)
    if cube.shape == (N_LAYERS, N_REGISTERS, N_BITS):
        for layer in cube:
            for line in layer:
                new_cube.append(conv2byte(line))
    else:
        for line in cube:
            new_cube.append(conv2byte(line))

    new_cube = bytearray(new_cube)
    return new_cube

def connect_cube():
    '''Connects to the cube. Searches the connected ports for something with
    "Arduino" in its description, then connects to it.

    USAGE:
        arduino = connect_cube()
        cube = np.ones(8,8,8)
        send_cube(arduino, cube)
    '''
    print("*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*")
    print("| SEARCHING FOR AN ARDUINO... |")
    print("*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*")

    ports = list(serial.tools.list_ports.comports())
    Arduino_ports=[]
    for p in ports:
        if p.pid == 29987:
            Arduino_ports.append(p)

    if len(Arduino_ports) == 0:
        raise Exception("no Arduino board detected")

    if len(Arduino_ports) > 1:
        print('Multiple Arduinos found - using the first')
    else:
        print("Arduino board detected")

    if len(Arduino_ports) >= 1:
        print(Arduino_ports[0].device)
        arduino = serial.Serial(Arduino_ports[0].device, BAUDRATE, timeout=.1)

    print("Waiting for Arduino to start...")
    time.sleep(2)
    print("\n\n\nReady to start transmitting!")

    return arduino

def send_cube(ser, cube):
    '''Send a 3D array to the cube, down the serial pipe.
    Returns the number of bits written. '''
    writeable_data = conv2byte_vect(cube)
    ser.write(writeable_data)

if __name__ in "__main__":
    data = np.zeros((N_LAYERS, N_REGISTERS, N_BITS), dtype=int)
    data[0,  :,  0] = 1
    data[0,  :, -1] = 1
    data[0,  0,  :] = 1
    data[0, -1,  :] = 1

    data[-1, :,  0] = 1
    data[-1, :, -1] = 1
    data[-1, 0,  :] = 1
    data[-1,-1,  :] = 1

    data[:,  0,  0] = 1
    data[:, -1,  0] = 1
    data[:,  0, -1] = 1
    data[:, -1, -1] = 1


    # Start the serial connection
    ser = connect_cube()
    send_cube(data)
    time.sleep(2)

    # Bouncing Box
    di = 1
    i = 1
    while True:
        if i == 6 or i == 0:
            di = -di
        i += di

        temp_data = np.zeros_like(data)
        temp_data[i:i+2, i:i+2, i:i+2] = 1

        # SEND THE DATA
        send_cube(ser, temp_data)

        # Wait for the human eye to catch up
        time.sleep(0.1)

    ser.close()
