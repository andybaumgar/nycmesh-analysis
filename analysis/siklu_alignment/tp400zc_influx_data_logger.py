import tp4000zc
from time import sleep

port = '/dev/cu.usbserial-10'

dmm = tp4000zc.Dmm(port=port)

while(True):
    sleep(.1)
    val = dmm.read()
    print(val.numericVal) # and the numeric value

dmm.close()