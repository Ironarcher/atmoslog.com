from random import randint
import time

colors = ['Red', 'Yellow', 'Green', 'Orange', 'Purple', 'White', 'Blue', 'Black', 'Grey']
counter = 0
ls = []
starttime = int(time.time())
while counter < 1000000:
	data = {
		"type" : "log",
		"value" : colors[randint(0,8)],
		"datetime" : int(time.time()),
	}
	ls.append(data)
	counter = counter + 1
print('done')
endtime = int(time.time())
finaltime = endtime - starttime
print(finaltime)
print(ls[9999])
