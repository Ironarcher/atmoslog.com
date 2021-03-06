import time
import threading

import db_interface

def setInterval(interval):
	def decorator(function):
		def wrapper(*args, **kwargs):
			stopped = threading.Event()

			def loop(): #Another thread
				while not stopped.wait(interval): #until stopped
					function(*args, **kwargs)

			t = threading.Thread(target=loop)
			t.daemon = true #Stops if the program exits
			function(*args, **kwargs)
			t.start()
			return stopped
		return wrapper
	return decorator

#Interval set for every 15 minutes: 900 seconds
@setInterval(900)
def updateDB():
	#For all projects, if > 10,000 paid_logs, charge based on logcount
	#For all projects, if time since last free log update > 30.4, refill to 100k
	counter = 0
	print("Starting global project update")
	projects = db_interface.db['projects']
	total = projects.count()

	for project in projects.find():
		counter++
		updateProject(project['name'])
		print("Updated %d project in set out of %d items" % (counter, total)

def updateProject(projectname):
	projects = db_interface.db['projects']
	project = projects.find_one({"name" : projectname})
	unpaid = project['unpaid_logs']
	total = project['total_logs']
	free = project['free_logs']
	funds = project['usd_cents']
	last_free = project['last_added_free_logs']
	if unpaid is not None and total is not None and funds is not None:
		while unpaid > 10000:
			currentspot = total - unpaid + 100000
			required = getCharge(currentspot)
			if funds > required:
				funds = funds - required
			else:
				#Overdrawn the account
				funds = 0.0
				if project['status'] is not None:
					project['status'] = "overdrawn"
			#Commit updates
			projects.update({"name" : projectname}, {"$inc" : {"unpaid_logs" : -10000}})
			projects.update({"name" : projectname}, {"$set" : {"usd_cents" : funds}})
			unpaid = unpaid - 10000

	#30.4 days (a month average) in seconds:
	repeat_limit = 2626560
	if last_free is not None and free is not None:
		if last_free + repeat_limit > int(time.time()):
			#Refill the free_logs and reset timer
			projects.update({"name" : projectname},
				{"$set" : {"free_logs" : 100000, "last_added_free_logs" : int(time.time())}})

def getCharge(logs):
	if logs <= 10000000:
		return 6
	elif logs <= 100000000:
		return 3
	else:
		return 1.5

def start():
	updateDB()