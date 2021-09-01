from paramiko import SSHClient
import os
import time
import sys
host=sys.argv[1]
user=sys.argv[2]
status = sys.argv[3]

if status=="rate":

	rate = sys.argv[4] 
	channel_string = sys.argv[5]
	start_th_string = sys.argv[6]
	stop_th_string = sys.argv[7]
	lead_string = sys.argv[8]
	tail_string = sys.argv[9]
	delay = sys.argv[10]
	print_status = sys.argv[11]

if status == "waveform":

	name_waveform = sys.argv[4] 
	channel_string = sys.argv[5]
	start_th_string = sys.argv[6]
	stop_th_string = sys.argv[7]
	lead_string = sys.argv[8]
	tail_string = sys.argv[9]


client = SSHClient()
client.load_system_host_keys()
client.connect(host, username=user)

os.system("python3 daqreadtcp_start.py &")

time.sleep(2)

channel_string = """ " """ + channel_string + """ " """
start_th_string = """ " """ + start_th_string + """ " """
stop_th_string = """ " """ + stop_th_string + """ " """
lead_string = """ " """ + lead_string + """ " """
tail_string= """ " """ + tail_string + """ " """



if status == "waveform" :
	os.system("nc 192.168.137.30 5000 > " + str(name_waveform) + " &")


	time.sleep(2)

	stdin, stdout, stderr = client.exec_command("bash daq_run_launch.sh -N "+channel_string+" -S "+start_th_string+" -P "+stop_th_string+" -L " + lead_string + " -T "+ tail_string)
	print ("stderr: ", stderr.readlines())
	print ( stdout.readlines())


if status == "rate":

	if print_status == "print":
		os.system("nc 192.168.137.30 5000 | ./RateParser -a -t "+str(rate)+" -d " +delay+ " -c 13 &")

	if print_status == "noprint":
		os.system("nc 192.168.137.30 5000 | ./RateParser -a -t "+str(rate)+" -d " +delay+ " >> rate_tmp.txt &")



	time.sleep(2)
	stdin, stdout, stderr = client.exec_command("bash daq_run_launch.sh -N "+channel_string+" -S "+start_th_string+" -P "+stop_th_string+" -L " + lead_string + " -T "+ tail_string)
	#print ("stderr: ", stderr.readlines())
	#print ( stdout.readlines())

