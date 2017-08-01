"""
Created on Wed Oct 5 15:00:07 2016

@author: khan
"""

import serial
import time
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
from datetime import datetime

ser=serial.Serial()
ser.baudrate = 57600
ser.port = 'COM5'
ser.timeout = 1
############### Note: Make sure Keithley is set to Terminator: <CR+LF>, RS-232, and 57600 baud

def WriteToFile(message,OutputFile):
    file = open(OutputFile+'.txt', 'a')
    file.write(message)
    file.close()

rootdir= 'C:\\Users\\python\\Desktop\\DIV Results'
savename = input("Please enter a unique name to save the file: ")
#savename = 'testing'
timestamp = time.time()
date_time = str(datetime.now())
first_time_seconds = str(math.floor(timestamp))

start_current = str(5)
stop_current = str(4)
current_step = str(-1e-1)
start_current_shunt = str(0.00011)
stop_current_shunt = str(0.00001)
current_step_shunt = str(-1e-5)
voltage_protection = str(10)
number_steps = str(11) #21 or fewer
number_steps_int = int(number_steps)
source_delay = str(0.01) # choose 10 ms for this to reduce heating
timeout_sec = str(float(number_steps) * float(source_delay) +1)

ser
ser.open()

ser.write(str.encode('*IDN?\n'))
ident = ser.read(200)
print (ident)

ser.reset_input_buffer()
ser.reset_output_buffer()

time.sleep(0.001)

ser.write(str.encode(':ROUT:TERM FRON\n'))
ser.write(str.encode(':ROUT:TERM?\n'))
print(ser.read(10))

ser.write(str.encode(':SENS:FUNC:CONC OFF\n'))
ser.write(str.encode(':SYST:RSEN ON\n')) # chooses 4wire measurement setting
ser.write(str.encode(':SOUR:FUNC CURR\n'))
ser.write(str.encode(":SENS:FUNC 'VOLT:DC'\n"))
ser.write(str.encode(':SENS:VOLT:PROT '+ voltage_protection+'\n'))
ser.write(str.encode(':SOUR:CURR:START '+ start_current_shunt+'\n')) # start current
ser.write(str.encode(':SOUR:CURR:STOP '+ stop_current_shunt+'\n')) # stop current
ser.write(str.encode(':SOUR:CURR:STEP ' + current_step_shunt+'\n')) #increment
ser.write(str.encode(':SOUR:CURR:MODE SWE\n'))
ser.write(str.encode(':SOUR:SWE:RANG AUTO\n'))
ser.write(str.encode(':SOUR:SWE:SPAC LIN\n'))
ser.write(str.encode(':TRIG:COUN ' + number_steps+'\n')) # number of points to measure
ser.write(str.encode(':SOUR:DEL ' + source_delay+'\n')) # source delay in sec
ser.write(str.encode(':OUTP ON\n')) #starts the sweep
ser.write(str.encode(':READ?\n')) #requests the data from the 2440

# get all of the data out
b = bytes.decode(ser.readline()) #super important because it reads the entire buffer rather than just the number of bytes you specify in the read() command
#print (b)
b = b.split(',') #turns this into an array instead of a string with a bunch of commas
print (len(b))
##print b
DIVoutput = np.zeros((int(len(b))//5,6))
Header = ['Rs Voltage (V)', 'Rs Current (A)', 'Series Resistance (mohm)', 'Rsh Voltage (V)', 'Rsh Current (A)', 'Shunt Resistance (ohm)']

for i in range(len(b)//5):
    DIVoutput[i,3] = b[i*5] # voltages
    DIVoutput[i,4] = b[i*5+1] #current

for i in range(len(b)//5-1):
    DIVoutput[i+1,5] = (DIVoutput[i+1,3] - DIVoutput[i,3]) / (DIVoutput[i+1,4] - DIVoutput[i,4])

RSH_MEAN = sum(DIVoutput[1:-1,5]) / float(len(DIVoutput[1:-1,5]))
print (savename)
print ("Rsh Mean")
print (RSH_MEAN)

##ser
##ser.open()

##ser.write(str.encode('*IDN?\n')
##ident = ser.read(200)
##print ident
time.sleep(0.25)

ser.reset_input_buffer()
ser.reset_output_buffer()

time.sleep(0.001)

ser.write(str.encode(':ROUT:TERM FRON\n'))
ser.write(str.encode(':ROUT:TERM?\n'))
print(ser.read(10))

ser.write(str.encode(':SENS:FUNC:CONC OFF\n'))
ser.write(str.encode(':SYST:RSEN ON\n')) # chooses 4wire measurement setting
ser.write(str.encode(':SOUR:FUNC CURR\n'))
ser.write(str.encode(":SENS:FUNC 'VOLT:DC'\n"))
ser.write(str.encode(':SENS:VOLT:PROT '+ voltage_protection+'\n'))
ser.write(str.encode(':SOUR:CURR:START '+ start_current+'\n')) # start current
ser.write(str.encode(':SOUR:CURR:STOP '+ stop_current+'\n')) # stop current
ser.write(str.encode(':SOUR:CURR:STEP ' + current_step+'\n')) #increment
ser.write(str.encode(':SOUR:CURR:MODE SWE\n'))
ser.write(str.encode(':SOUR:SWE:RANG AUTO\n'))
ser.write(str.encode(':SOUR:SWE:SPAC LIN\n'))
ser.write(str.encode(':TRIG:COUN ' + number_steps+'\n')) # number of points to measure
ser.write(str.encode(':SOUR:DEL ' + source_delay+'\n')) # source delay in sec
ser.write(str.encode(':OUTP ON\n')) #starts the sweep
ser.write(str.encode(':READ?\n')) #requests the data from the 2440

# get all of the data out
a = bytes.decode(ser.readline()) #super important because it reads the entire buffer rather than just the number of bytes you specify in the read() command
a = a.split(',') #turns this into an array instead of a string with a bunch of commas

# clean up the 2440 and the port (turn off output and close port)
ser.write(str.encode(':OUTP OFF\n'))
ser.close()


Header = ['Rs Voltage (V)', 'Rs Current (A)', 'Series Resistance (mohm)', 'Rsh Voltage (V)', 'Rsh Current (A)', 'Shunt Resistance (mohm)']

for i in range(len(a)//5):
    DIVoutput[i,0] = a[i*5] # voltages
    DIVoutput[i,1] = a[i*5+1] #current

for i in range(len(a)//5-1):
    DIVoutput[i+1,2] = 1000 * (DIVoutput[i+1,0] - DIVoutput[i,0]) / (DIVoutput[i+1,1] - DIVoutput[i,1])

RS_MIN = min(DIVoutput[1:-1,2])
print ("Rs min (m-ohm)")
print (RS_MIN)
print ("")

time.sleep(0.25)
#################  Rsh is below


##
### clean up the 2440 and the port (turn off output and close port)
##ser.write(str.encode(':OUTP OFF\n')
##ser.close()

font = {'family' : 'sans-serif',
        'weight' : 'bold',
        'size'   : 16}
title_font = {'fontname':'Arial', 'size':'12', 'color':'black', 'weight':'normal',
          'verticalalignment':'bottom'} # Bottom vertical alignment for more space
matplotlib.rc('font', **font)


fig, ax1 = plt.subplots()

ax1.plot(DIVoutput[:,0],DIVoutput[:,1], 'b.')
ax1.set_xlabel('V (V)')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('I (A)', color='b')
for tl in ax1.get_yticklabels():
    tl.set_color('b')


ax2 = ax1.twinx()
#s2 = np.sin(2*np.pi*t)
ax2.plot(DIVoutput[1:,0],DIVoutput[1:,2], 'r.')
ax2.set_ylabel('Rs (Ohms)', color='r')
for tl in ax2.get_yticklabels():
    tl.set_color('r')
plt.title(savename)
##plt.show()
output = str(savename)+","+str(RS_MIN)+","+str(RSH_MEAN)+","+str(date_time)+"\n"
##WriteToFile("SampleID, Rs_min (mohm), Rsh_mean (ohm)\n",rootdir + '\\data\\SummaryFile')
WriteToFile(output,rootdir + '\\data\\SummaryFile')
fig.savefig(rootdir+ '\\data\\' + savename+'.png',bbox_inches='tight')
np.savetxt(rootdir + '\\data\\' + savename + '.txt', DIVoutput)