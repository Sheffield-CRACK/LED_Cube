import gpiozero
import time

data = gpiozero.DigitalOutputDevice(17, initial_value=False)
clock = gpiozero.DigitalOutputDevice(18, initial_value=False)


data.off()

clock.on()
time.sleep(0.100) # 100ms
clock.off()
time.sleep(0.100)

data.on()

clock.on()
time.sleep(0.100) # 100ms
clock.off()
time.sleep(0.100)




data.off()
clock.off()
