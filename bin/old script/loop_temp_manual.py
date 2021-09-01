import sys 
import os
import time

loop=10
channels=str("0")
name="temp_calibrazione_cold_ch"+channels+".txt"



while(1):

	os.system("""ssh root@192.168.137.30 'bash get_param.sh -N " """+channels+ """ "' >>"""+ name)
	time.sleep(int(loop))
