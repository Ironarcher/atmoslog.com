from pymongo import MongoClient
import time
from random import randint

def stress():
	colors = ['Red', 'Yellow', 'Green', 'Orange', 'Purple', 'White', 'Blue', 'Black', 'Grey']
	counter = 0
	ls = []
	while counter < 1000000:
		data = {
			"type" : "log",
			"value" : colors[randint(0,8)],
			"datetime" : int(time.time()),
		}
		ls.append(data)
		counter = counter + 1
	return ls

c = MongoClient('localhost', 27017)
db = c['test']

counter = 0
coll = db['size1']

print("Starting")
starttime = int(time.time())

while counter < 1:
	coll.insert_many(stress())
	print(counter*1000000)
	time.sleep(0.1)
	counter = counter + 1

endtime = int(time.time())
finaltime = endtime - starttime
print("Program complete")
print("Took %s seconds" % finaltime)
