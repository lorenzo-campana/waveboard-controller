import sys 
import os
import time

loop=int(sys.argv[1])-2
name=sys.argv[2]

channels=sys.argv[3]

while(1):

	os.system("""ssh root@192.168.137.30 'bash get_param.sh -N " """+channels+ """ "' >>"""+ name)
	time.sleep(int(loop))

