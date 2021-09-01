import numpy as np 
import tkinter  
import matplotlib
import matplotlib.pyplot as plt 
import random
import sys

single_channel_status = sys.argv[1]
if single_channel_status=="True":
	single_channel_status=True
else:
	single_channel_status=False

all_channel_status = sys.argv[2]
if all_channel_status=="True":
	all_channel_status=True
else:
	all_channel_status=False

filename = sys.argv[3]
channel = sys.argv[4]

data = np.genfromtxt(filename, dtype=str)


if all_channel_status:

	histo={}

	for ch in np.arange(1,13):
		histo[ch]=np.diff(data[data[:,0]=="0:0:"+str(ch),1].astype(int))		
	print(histo[1])
	fig,ax=plt.subplots(3,4)
	fig.set_size_inches(16,8)
	plt.tight_layout(pad=2, w_pad=2, h_pad=3.5)

	ch=1
	for row in ax:
		for column in row:
			column.hist(histo[ch],bins='auto',alpha=0.5)
			column.set_title("time difference ch "+str(ch))
			column.set_xlabel("Time difference (ns)")
			column.set_ylabel("# events")
			ch=ch+1

	plt.show()
	plt.draw()

elif single_channel_status:
	histo=np.diff(data.astype(int))
	fig,ax=plt.subplots()
	ax.hist(histo,bins='auto')	
	ax.set_xlabel("Time difference (ns)")
	ax.set_ylabel("# events")	
	ax.set_title("Time difference histogram of ch "+channel)
	plt.show()