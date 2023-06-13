# load the module
import tp4000zc

# the port that we're going to use.  This can be a number or device name.
# on linux or posix systems this will look like /dev/tty2 or /dev/ttyUSB0
# on windows this will look something like COM3
port = '/dev/ttyUSB0'

# get an instance of the class
dmm = tp4000zc.Dmm(port)

# read a value
val = dmm.read()

print val.text       # print the text representation of the value
                     # something like: -4.9 millivolts DC
print val.numericVal # and the numeric value
                     # ie: -0.0048
# recycle the serial port
dmm.close()