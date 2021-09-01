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


count=0

random_status = sys.argv[1]
if random_status=="True":
	random_status=True
else:
	random_status=False

beginning_status = sys.argv[2]
if beginning_status=="True":
	beginning_status=True
else:
	beginning_status=False

overlap_status = sys.argv[3]
if overlap_status=="True":
	overlap_status=True
else:
	overlap_status=False

amplitude_status = sys.argv[4]
if amplitude_status=="True":
	amplitude_status=True
else:
	amplitude_status=False

amplitude_text = float(sys.argv[5])

amplitude_filter = sys.argv[6]

single_channel_status = sys.argv[7]
if single_channel_status=="True":
	single_channel_status=True
else:
	single_channel_status=False

all_channel_status = sys.argv[8]
if all_channel_status=="True":
	all_channel_status=True
else:
	all_channel_status=False


filename=sys.argv[9]

single_ch = int(sys.argv[10])



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


if all_channel_status:

	data_ch={}

	for ch in np.arange(1,13):

		data_ch[ch]=data_array[data_array[:,0]=="0:0:"+str(ch) ,1:]


	def onclick(event):
		global count

		if overlap_status == False:

			for row in ax:
				for column in row:
					column.clear()

		index=[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,3)]

		if event.button == 1:
			for ch in np.arange(1,13):
				if random_status:
					if len(data_ch[ch]!=0):

						n=random.randint(0,len(data_ch[ch]))	
						ax[index[ch-1]].plot(4*np.arange(len(data_ch[ch][n,data_ch[ch][n]!=None].astype(int))), convert_adc_to_v(data_ch[ch][n,data_ch[ch][n]!=None].astype(int),ch-1))
						ax[index[ch-1]].grid(True)
						ax[index[ch-1]].set_title("Waveform # "+str(n)+" ch "+str(ch))
						ax[index[ch-1]].set_xlabel("Time (ns)")
						ax[index[ch-1]].set_ylabel("Amplitude (mV)")

				elif random_status == False:	
					if len(data_ch[ch]!=0) and count<len(data_ch[ch]):

						ax[index[ch-1]].plot(4*np.arange(len(data_ch[ch][count,data_ch[ch][count]!=None].astype(int))), convert_adc_to_v(data_ch[ch][count,data_ch[ch][count]!=None].astype(int),ch-1))
						ax[index[ch-1]].grid(True)

						ax[index[ch-1]].set_xlabel("Time (ns)")
						ax[index[ch-1]].set_ylabel("Amplitude (mV)")
						ax[index[ch-1]].set_title("Waveform # "+str(count)+" ch "+str(ch))
						
					else:
						pass
					
		plt.draw() #redraw
		count=count+1

	count = 0
	fig,ax=plt.subplots(3,4)
	fig.set_size_inches(16,8)

	plt.tight_layout(pad=2, w_pad=2, h_pad=3.5)
	fig.canvas.mpl_connect('button_press_event',onclick)
	plt.show()
	plt.draw()


if single_channel_status:
	if random_status:
		data_format=[]

		for x in data[1:]:
			temp = split(x,('\t'))
			temp_int = list(map(int,temp[:-1]))
			
			if amplitude_status:
				if amplitude_filter == "more_than":
					if max(temp_int) >= convert_v_to_adc(float(amplitude_text),(single_ch)):
						data_format.append(temp_int)
				else:
					if max(temp_int) <= convert_v_to_adc(float(amplitude_text),(single_ch)):
						data_format.append(temp_int)

			else:
				data_format.append(temp_int)

		x=[]
		y=[]


		def onclick_random(event):
			if event.button == 1:
				n=random.randint(0,len(data_format)-1)
				y=data_format[n]
				y_converted= [convert_adc_to_v(element,single_ch)  for element in y]
				x=range(0,len(y))
				#clear frame
			if overlap_status == False:
				plt.clf()
			ax = plt.gca()
			ax.set_title("waveform # "+ str(n))
			ax.set_ylabel("Amplitude (V)")
			ax.set_xlabel("Time (ns)")
			plt.grid(True)
			plt.plot([element * 4 for element in x],y_converted); #inform matplotlib of the new data
			plt.draw() #redraw

		fig,ax=plt.subplots()
		ax.plot(x,y)
		fig.canvas.mpl_connect('button_press_event',onclick_random)
		plt.show()
		plt.draw()


	elif beginning_status:
		data_format=[]

		for x in data[1:]:
			temp = split(x,('\t'))
			temp_int = list(map(int,temp[:-1]))
			
			if amplitude_status:
				if amplitude_filter == "more_than":
					if  max(temp_int) >=convert_v_to_adc(float(amplitude_text),(single_ch)):
						data_format.append(temp_int)
				elif amplitude_filter == "less_than":
					if max(temp_int) <= convert_v_to_adc(float(amplitude_text),(single_ch)):
						data_format.append(temp_int)

			else:
				data_format.append(temp_int)

		x=[]
		y=[]
		
		def onclick_beginning(event):
			global count

			if event.button == 1:
				y=data_format[count]
				y_converted= [convert_adc_to_v(element,single_ch) for element in y]
				x=range(0,len(y))
			#clear frame
			if overlap_status == False:
				plt.clf()

			ax = plt.gca()
			ax.set_title("waveform # "+ str(count))
			ax.set_ylabel("Amplitude (mV)")
			ax.set_xlabel("Time (ns)")
			plt.grid(True)
			plt.plot([element *4 for element in x],y_converted)
			plt.draw() #redraw
			count = count + 1 

		fig,ax=plt.subplots()
		ax.set_title("waveform # "+ str(count))
		ax.set_ylabel("Amplitude (mV)")
		ax.set_xlabel("Time (ns)")
		plt.plot(x,y)
		fig.canvas.mpl_connect('button_press_event',onclick_beginning)
		plt.show()
		plt.draw()