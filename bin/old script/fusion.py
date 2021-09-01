import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import time
from config import *
import os
import sys
 
name=sys.argv[1]


name_rate = "rate_tmp.txt"
name_param = "param_tmp.txt"

data_rate = np.genfromtxt(name_rate, dtype="str", delimiter=":")
data_param = np.genfromtxt(name_param,dtype="str", delimiter="\t")


rate_ch = data_rate[:,0]
rate_ch=np.array([string.replace(" ","") for string in rate_ch])
print(rate_ch)



param_ch = data_param[:,1]

rate = np.array([string.split(" ")[-2] for string in data_rate[:,1]])
rate_list=[]
for i in rate:
	rate_list.append(round(float(i[:-2]),1))
rate=np.array(rate_list)
print(rate.size)


rate_time=np.array([string.split(" ")[-1] for string in data_rate[:,1]]).astype(float)
print(rate_time)

param_time = data_param[:,0][data_param[:,0]!=''].astype(int)

temp=data_param[:,2][data_param[:,2]!=''].astype(float)


start_th=data_param[:,3][data_param[:,3]!='']


start_th_list = []
for i in start_th:
	start_th_list.append(int(i,16))
start_th = np.array(start_th_list)

stop_th=data_param[:,4][data_param[:,4]!='']
stop_th_list = []
for i in stop_th:
	stop_th_list.append(int(i,16))
stop_th = np.array(stop_th_list)


v_bias=data_param[:,5][data_param[:,5]!=''].astype(float)





for i in np.arange(0,12):
	start_th_final=[]
	stop_th_final=[]
	v_bias_final=[]
	temp_final=[]
	ch_final=[]


	ch="ch:"+str(i)
	start_th_conv = np.around((adc_to_v[i][1]+(int(0x3fff)-start_th)*adc_to_v[i][0])*1000,1)
	stop_th_conv = np.around((adc_to_v[i][1]+(int(0x3fff)-stop_th)*adc_to_v[i][0])*1000,1)
	print(rate_time[rate_ch=="Ch"+str(i)])


	for time in rate_time[rate_ch=="Ch"+str(i)]:
		index = np.argmin(np.abs(param_time[param_ch==ch]-time))
		start_th_final.append(start_th_conv[param_ch==ch][index])
		stop_th_final.append(stop_th_conv[param_ch==ch][index])
		v_bias_final.append(v_bias[param_ch==ch][index])
		temp_final.append(temp[param_ch==ch][index])

	start_th_final=np.array(start_th_final)
	stop_th_final=np.array(stop_th_final)
	v_bias_final=np.array(v_bias_final)
	temp_final=np.array(temp_final)
	
	print(rate_ch[rate_ch=="Ch"+str(i)].size,start_th_final.size,stop_th_final.size,temp_final.size,rate_time[rate_ch=="Ch"+str(i)].size,v_bias_final.size)

	if rate_time[rate_ch=="Ch"+str(i)].size !=0:
		file_save=np.concatenate((rate_ch[rate_ch=="Ch"+str(i)], np.around(rate_time[rate_ch=="Ch"+str(i)],0).astype(int), rate[rate_ch=="Ch"+str(i)], temp_final, start_th_final,stop_th_final,v_bias_final ))
		file_save = file_save.reshape(7,rate_ch[rate_ch=="Ch"+str(i)].size).T
		file_save=np.savetxt(name[:-4]+"_ch"+str(i)+".txt", file_save, fmt=['%s', '%s','%s','%s','%s','%s','%s',], delimiter='\t', header="channel\ttimestamp\tCPS\ttemperature\tstart_th\tstop_th\tv_bias")



os.system("rm param_tmp.txt")
os.system("rm rate_tmp.txt")
