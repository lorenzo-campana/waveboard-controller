import numpy as np 
import matplotlib.pyplot as plt 
import random
import sys
from config import *



# v_to_adc=[14610.97046824,86.995335136]

v_to_adc={0: [14478.60239767,   105.72266231],
 10: [14581.95209726,    94.49772418],
 11: [14585.64212614,    71.52928685],
 2: [14550.19800913,    99.07229959],
 3: [14705.41800247,   120.3148473 ],
 4: [14543.1833827,   140.8470843],
 5: [14575.71114986,    83.09878558],
 6: [14502.89628843,   125.51115324],
 7: [14756.93105566,   122.49110006],
 8: [14692.74249293,    64.11840958],
 9: [14916.64285453,  -109.3580361 ],
 1: [0,0]}


adc_to_v = {0: [ 6.90587395e-05, -7.26334767e-03],
 10: [ 6.85696081e-05, -6.44335609e-03],
 11: [ 6.85478977e-05, -4.84780842e-03],
 2: [ 6.87168601e-05, -6.76119351e-03],
 3: [ 6.79912680e-05, -8.13244616e-03],
 4: [ 6.87547827e-05, -9.65797908e-03],
 5: [ 6.85985462e-05, -5.66229944e-03],
 6: [ 6.89460406e-05, -8.62872222e-03],
 7: [ 6.77535565e-05, -8.24966102e-03],
 8: [ 6.80533062e-05, -4.33043723e-03],
 9: [6.70308781e-05, 7.36760090e-03],
 1: [0,0]}


count=0

pedestal_element= int(sys.argv[2])
filename=sys.argv[1]

single_channel_status=(sys.argv[3])
channel_number=sys.argv[4]

if single_channel_status == "True":
    single_channel_status=True
else:
    single_channel_status=False



def convert_adc_to_v(element,ch):
    return ((adc_to_v[ch][1]+element*adc_to_v[ch][0])*1000)

def convert_v_to_adc(element,ch):
    return (v_to_adc[ch][1]+element*v_to_adc[ch][0])

with open(filename) as a:
    data = a.read().splitlines()

def split(txt, seps):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

data_split=[]

for i in data:
    temp = split(i,('\t'))
    data_split.append(temp)

length = max(map(len, data_split))
data_array=np.array([xi+[None]*(length-len(xi)) for xi in [sublist[0:-1] for sublist in data_split]])
#					 metto None dove non ho dati 		   levo il " " dai dati

amplitude_status=False
data_format_a=[]

low_value=0.021
high_value=100

for x in data[1:]:
    temp = split(x,('\t'))
    temp_int = list(map(int,temp[:-1]))
    if amplitude_status:
        if  max(temp_int)>=convert_v_to_adc(float(low_value),(single_ch)) and max(temp_int)<=convert_v_to_adc(float(high_value),(single_ch)):
            data_format_a.append(temp_int)
    else:
        data_format_a.append(temp_int)

channel_number="5"
pedestal_element=0
cut=None  #None if no cut
pedestal_sub=False

histo_charge=[]
histo_amplitude=[]
histo_lenght=[]


if len(data_format_a)!=0:
    for event in np.array(data_format_a,dtype="object")[1:]:
        event=np.array(event)[:cut]
        event=np.array([ convert_adc_to_v(i,int(channel_number)) for i in event[event!=None].astype(int)])

        if pedestal_sub==True:
            value_charge=event.sum()-(event[0:pedestal_element].mean()*len(event))
        else:
            value_charge=event.sum()
        
        value_amplitude=np.abs(event.max())
        value_lenght=(event.size)*4
        
        histo_lenght.append(value_lenght)
        histo_amplitude.append(value_amplitude)
        histo_charge.append(value_charge)

        
fig,ax=plt.subplots()
ax.hist(histo_charge,bins=200)
ax.set_xlabel("Charge (pC)")
ax.set_ylabel("# events")
ax.set_title("Charge histogram ch "+ channel_number)
plt.grid()
plt.show() 

        
fig,ax=plt.subplots()
ax.hist(histo_amplitude,bins=100)
ax.set_xlabel("Maximum (mV)")
ax.set_ylabel("# events")
ax.set_title("Histogram of the maximum ch "+ channel_number)
plt.grid()
plt.show() 



fig,ax=plt.subplots()
ax.hist(histo_lenght,bins=80)
ax.set_xlabel("duration (ns)")
ax.set_ylabel("# events")
ax.set_title("Duration histogram ch "+ channel_number)
plt.grid()
plt.show() 

        

x=[]
y=[]

def onclick_beginning_a(event):
    global count
    if event.button == 1:
        y=data_format_a[count][:cut]
        y_converted= [convert_adc_to_v(element,single_ch) for element in y]
        x=range(0,len(y))
    #clear frame
    if overlap_status == False:
        plt.clf()

    ax1 = plt.gca()
    ax1.set_title("waveform # "+ str(count))
    ax1.set_ylabel("Amplitude (mV)")
    ax1.set_xlabel("Time (ns)")
    plt.grid(True)
    ax1.plot([element *4 for element in x],y_converted)
    plt.draw() #redraw
    count = count + 1 

fig,ax1=plt.subplots()
ax1.set_title("waveform # "+ str(count))
ax1.set_ylabel("Amplitude (mV)")
ax1.set_xlabel("Time (ns)")
ax1.plot(x,y)
fig.canvas.mpl_connect('button_press_event',onclick_beginning_a)
plt.show()
