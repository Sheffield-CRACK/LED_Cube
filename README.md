# Trackellite
Software for desktop satellite tracking toy. 
Will query for TLE files daily, and produce a grid of how many satellites are where in real time. This uses an arduino and a series of SIPO shift registers to drive the actual cube. The python script `send_cube.py` contains a function, `conv2byte_vect`, which converts a numpy array (or list) to something that can be transmitted to the arduino. Something like this:

```python
# Start the serial connection
ser = serial.Serial('/dev/cu.wchusbserial72', 9600, timeout=.1)
print("Waiting for Arduino to start...")
time.sleep(2)
print("\n\n\nReady to start transmitting!")


# Bouncing Box
di = 1
i = 1
while True:
    if i == 6 or i == 0:
        di = -di
    i += di

    temp_data = np.array(data, copy=True)
    temp_data[i:i+2, i:i+2, i:i+2] = 1

    writeable_data = conv2byte_vect(temp_data)
    ser.write(writeable_data)

    time.sleep(0.1)

ser.close()
```

## TLE, and the basics of the Raspberry Pi's job
This is how satellite/orbital junk ephemerides are reported. It's basically just the position of the thing at two moments in time, then you extrapolate out from there. I'm using ported NASA code to do this - if it's good enough for NASA it's good enough for me, and I cant be arsed to write the code for that. They're somehow still using a system built to work with punchcards? Fortran users must feel vindicated.

Once a day, the full list of TLE files from [here](https://celestrak.com/NORAD/elements/) is downloaded, and each is checked to see if it passes overhead to the user. If it does, the pi puts it in its pocket, but if it doesn't it gets chucked away. Then, the pi starts constantly checking what's overhead and generating a grid, with the number of objects in each cell. The grid corresponds to the volume of space above the user. The plan is to then use this to light up the grid, corresponding to how the space junk is positioned above the user.



# Checklist:
- [DONE] [SLOW, DONT USE] Query N2YO for satellites
- [DONE] Compute my own satellite locations
- [DONE] Figure out how to plug the grid into LED matrix
  - LED matrix, c.f. [here](https://www.instructables.com/id/Led-Cube-8x8x8/)?
- [DONE] Get the software running on a raspberry pi (3B+? or will a zero work?)
- Breadboard a prototype LED matrix [DONE] and control it [TODO]
  - This needs to be done differently. I was going to do it straight off the pi, but thinking about it, it'd be better to have one (or several) arudinos handle the LEDs, so that the pi can focus on the satellites. An arduino MEGA has like, 56 GPIO pins or something, so one of those could easily handle a 4x5x5 grid (4 + 25 pins needed). Slap some transistors on that and we'd be good to go I think, though I'd probably want a breadboard hat for the arduino, vs *learning how to make a PCB(!!)* and getting that manufactured. And there's no way I'm doing this with loose wires.
- [DONE] Wire together a 3D grid of LEDs
  - I bought some stainless steel wire to use as conductor and scaffold - but solder doesn't stick to it >:(
  - I need something else. Bare steel wire maybe? Or use the scaffold and wrap a current carrier around it? [This worked]
- [DONE] Control the cube from python, through the arduino driver.
- [lol] Make a nice case
- Add a screen? Links to satellites on web trackers for more info?

