import gpiozero
import time

PULSE_WIDTH = 100/1000
DELAY = 5


data = gpiozero.DigitalOutputDevice(17, initial_value=False)
clock = gpiozero.DigitalOutputDevice(18, initial_value=False)

print("Okay, going")

data.off()
print("Data off, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Sent!")
time.sleep(DELAY)

data.on()
print("Data on, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Done!")
time.sleep(DELAY)

data.off()
print("Data off, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Sent!")
time.sleep(DELAY)

data.on()
print("Data on, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Done!")
time.sleep(DELAY)

data.off()
print("Data off, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Sent!")
time.sleep(DELAY)

data.on()
print("Data on, sending clock pulse")
clock.on()
time.sleep(PULSE_WIDTH) # 100ms
clock.off()
print("Done!")
time.sleep(DELAY)



print("Setting data and clock both to off")
data.off()
clock.off()
