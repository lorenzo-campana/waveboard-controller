import numpy as np 
import matplotlib.pyplot as plt 
import random
import sys
from config import *

# v_to_adc=[14610.97046824,86.995335136]

v_to_adc={0: [14430.73809026,   124.91599012],
 10: [14533.77479962,   113.81947924],
 11: [14537.55211506,    90.82617243],
 2: [14502.20029638,   118.32964066],
 3: [14656.90727969,   139.77791547],
 4: [14494.9997035 ,   160.15769568],
 5: [14527.52394762,   102.4214024 ],
 6: [14454.87181351,   144.7605746 ],
 7: [14708.26384998,   142.01832373],
 8: [14644.1256618 ,    83.60895255],
 9: [14867.30919883,   -89.57767131],
 1: [0, 0]}

# adc_to_v = [6.8441e-5,-5.952176e-3]


adc_to_v = {0: [ 6.92916828e-05, -8.63473619e-03],
 10: [ 6.88010372e-05, -7.81258421e-03],
 11: [ 6.87797242e-05, -6.21374097e-03],
 2: [ 6.89491412e-05, -8.13307659e-03],
 3: [ 6.82210919e-05, -9.50894388e-03],
 4: [ 6.89861968e-05, -1.10351793e-02],
 5: [ 6.88299283e-05, -7.02824810e-03],
 6: [ 6.91782215e-05, -1.00030084e-02],
 7: [ 6.79826390e-05, -9.62683732e-03],
 8: [ 6.82826500e-05, -5.69100416e-03],
 9: [6.72568850e-05, 6.04598315e-03],
 1: [0,0]}


pedestal_element= int(sys.argv[2])
filename=sys.argv[1]

single_channel_status=(sys.argv[3])
channel_number=sys.argv[4]
pedestal_status=sys.argv[5]
histo_filter=sys.argv[6]

if pedestal_status == "True":
	pedestal_sub=True
else:
	pedestal_sub=False


if single_channel_status == "True":
	single_channel_status=True
else:
	single_channel_status=False


with open(filename) as a:
	data = a.read().splitlines()

def convert_adc_to_v(element,ch):
	return (adc_to_v[ch][1]+element*adc_to_v[ch][0])

def convert_v_to_adc(element,ch):
	return (v_to_adc[ch][1]+element*v_to_adc[ch][0])

def split(txt, seps):
	default_sep = seps[0]

	# we skip seps[0] because that's the default separator
	for sep in seps[1:]:
		txt = txt.replace(sep, default_sep)
	return [i.strip() for i in txt.split(default_sep)]

data_split=[]

for i in data:
	temp = split(i,('\t'))
	data_split.append(temp)

length = max(map(len, data_split))
data_array=np.array([xi+[None]*(length-len(xi)) for xi in [sublist[0:-1] for sublist in data_split]])
					 #metto None dove non ho dati 		   levo il " " dai dati

# amplitude_status=False
# data_array=[]

# for x in data:
#     temp = split(x,('\t'))
#     temp_int = list(map(int,temp[:-1]))
#     if amplitude_status:
#         if  max(temp_int)>=convert_v_to_adc(float(low_value),(single_ch)) and max(temp_int)<=convert_v_to_adc(float(high_value),(single_ch)):
#             data_array.append(temp_int)
#     else:
#         data_array.append(temp_int)



if single_channel_status:
	cut=None  #None if no cut

	histo_charge=[]
	histo_amplitude=[]
	histo_lenght=[]


	if len(data_array)!=0:
	    for event in np.array(data_array,dtype="object")[1:]:
	        event=np.array(event)[:cut]
	        event=event[event!=None].astype(int)

	        if pedestal_sub==True:
	            value_charge=event.sum()-(event[0:pedestal_element].mean()*len(event))
	        else:
	            value_charge=event.sum()
	        
	        value_amplitude=convert_adc_to_v(np.abs(event.max()), int(channel_number))
	        value_lenght=(event.size)*4
	        
	        value_charge= (value_charge * adc_to_v[int(channel_number)][0]) + event.size*adc_to_v[int(channel_number)][1]
	        histo_lenght.append(value_lenght)
	        histo_amplitude.append(value_amplitude)
	        histo_charge.append(value_charge)

	if histo_filter=="Charge":
		fig,ax=plt.subplots()
		ax.hist(histo_charge,bins="auto")
		ax.set_xlabel("Charge (pC)")
		ax.set_ylabel("# events")
		ax.set_title("Charge histogram ch "+ channel_number)
		plt.grid()
		plt.show() 

	if histo_filter=="Maximum":
		fig,ax=plt.subplots()
		ax.hist(histo_amplitude,bins="auto")
		ax.set_xlabel("Maximum (V)")
		ax.set_ylabel("# events")
		ax.set_title("Histogram of the maximum ch "+ channel_number)
		plt.grid()
		plt.show() 

	if histo_filter == "Duration":
		fig,ax=plt.subplots()
		ax.hist(histo_lenght,bins="auto")
		ax.set_xlabel("duration (ns)")
		ax.set_ylabel("# events")
		ax.set_title("Duration histogram ch "+ channel_number)
		plt.grid()
		plt.show() 

else: #multichannel
	cut=None
	histo_lenght={}
	histo_charge={}
	histo_amplitude={}

	for ch in np.arange(1,13):
		histo_lenght[ch]=[]
		histo_charge[ch]=[]
		histo_amplitude[ch]=[]
		if len(data_array[data_array[:,0]=="0:0:"+str(ch) ,1:])!=0:
			for event in data_array[data_array[:,0]=="0:0:"+str(ch) ,1:]:

				event=np.array(event)[:cut]

				event=event[event!=None].astype(int)
				if pedestal_sub==True:
					value_charge=event.sum()-(event[0:pedestal_element].mean()*len(event))
				else:
					value_charge=event.sum()
				
				value_amplitude=convert_adc_to_v(np.abs(event.max()), int(ch))
				value_lenght=(event.size)*4
				
				value_charge= (value_charge * adc_to_v[int(ch)][0]) + event.size*adc_to_v[int(ch)][1]
				
				histo_lenght[ch].append(value_lenght)
				histo_amplitude[ch].append(value_amplitude)
				histo_charge[ch].append(value_charge)

	if histo_filter == "Charge":			
		fig,ax=plt.subplots(3,4)
		fig.set_size_inches(16,8)
		plt.tight_layout(pad=2, w_pad=2, h_pad=3.5)

		ch=1
		for row in ax:
			for column in row:
				column.hist(histo_charge[ch],bins='auto',alpha=0.8)
				column.set_title("ch "+str(ch))
				column.set_xlabel("Charge (pC)")
				column.set_ylabel("# events")
				ch=ch+1

		plt.show()
		plt.draw()

	if histo_filter == "Duration":			
		fig,ax=plt.subplots(3,4)
		fig.set_size_inches(16,8)
		plt.tight_layout(pad=2, w_pad=2, h_pad=3.5)

		ch=1
		for row in ax:
			for column in row:
				column.hist(histo_lenght[ch],bins='auto',alpha=0.8)
				column.set_title("ch "+str(ch))
				column.set_xlabel("Duration (ns)")
				column.set_ylabel("# events")
				ch=ch+1

		plt.show()
		plt.draw()

	if histo_filter == "Maximum":			
		fig,ax=plt.subplots(3,4)
		fig.set_size_inches(16,8)
		plt.tight_layout(pad=2, w_pad=2, h_pad=3.5)

		ch=1
		for row in ax:
			for column in row:
				column.hist(histo_amplitude[ch],bins='auto',alpha=0.8)
				column.set_title("ch "+str(ch))
				column.set_xlabel("Maximum (V)")
				column.set_ylabel("# events")
				ch=ch+1

		plt.show()
		plt.draw()