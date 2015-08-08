import random
import time
import re
from pymongo import MongoClient
import pymongo
from bson.son import SON
from bisect import bisect_left

c = MongoClient('localhost', 27017)
db = c['atmos_final']

tableBlacklist = ['projects']
maximumlength = 50

def randKey(digits):
	return ''.join(random.choice(
		'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(digits))

#Table types: qualitative, quantitative_discrete, quantitative_continuous
def createTable(ownerproject, tablename, tabletype):
	if re.match('^\w+$', tablename) is None:
		print('Only alphanumeric characters and underscores can be included in the table name.')
		return
	elif len(tablename) > maximumlength:
		print('Maximum length of the table name is 50 characters.')
		return
	elif tabletype != "qualitative" and tabletype != "quantitative_discrete" and tabletype != "quantitative_continuous":
		print('Tabletype incorrect')
		return

	projects = db['projects']
	projectfile = projects.find_one({"name" : ownerproject})
	if projectfile is not None:
		name = ownerproject + "-" + tablename
		if name not in db.collection_names():
			db.create_collection(name)
			description = {"type" : "description",
						   "tabletype" : tabletype,
						   "duplicate_loss" : 0,
						   "invalid_api_key" : 0,
						   "server_error" : 0,
						   "misc_error" : 0,
						   "datecreated" : int(time.time()),
						  }
			col = db[name]
			col.insert_one(description)

			tablelist = projectfile['tables']
			updatedtablelist = tablelist.append(tablename)
			#In the project description, add this table
			projects.update({'name' : 'ownerproject'}, {"$set" : {"tables" : updatedtablelist}}, upsert=False)
		else:
			print("Error: Table name in this project already exists. Choose a different name.")
	else:
		print("Error: Owner proejct does not exist")

#Access setting: Either public or private
#Status setting: running, overdrawn, stopped
def createProject(name, creator, access, description):
	if re.match('^\w+$', name) is None:
		print('Only alphanumeric characters and underscores can be included in the project name.')
		return
	elif len(name) > maximumlength:
		print('Maximum length of the project name is 50 characters.')
		return

	projects = db['projects']
	key = randKey(20)
	while(projects.find_one({"secret_key" : key})) is not None:
		key = randKey(20)

	if projects.find_one({"name" : name}) is None:
		doc = {"name" : name,
			   "description" : description,
			   "tables" : [name + '-log'],
			   "admins" : [creator],
			   "contributors" : [creator],
			   "readers" : [creator],
			   "access" : access,
			   "secret_key" : key,
			   "usd_cents" : 0.0,
			   "unpaid_logs" : 0,
			   "free_logs" : 100000,
			   "total_logs" : 0,
			   "status" : "running",
			   "popularity" : 0,
			   "default_tabletype" : "qualitative",
			   "datecreated" : int(time.time()),
			   "last_added_free_logs" : int(time.time())}
		projects.insert_one(doc)

		#Create the first table (called log)
		createTable(name, "log", "qualitative")
	else:
		print("Error: Project name already exists. Choose a different name.")

def updateProject(oldname, name, access, description, default_tabletype):
	if re.match('^\w+$', name) is None:
		print('Only alphanumeric characters and underscores can be included in the project name.')
		return
	elif len(name) > maximumlength:
		print('Maximum length of the project name is 50 characters.')
		return
	elif default_tabletype != "qualitative" and default_tabletype != "quantitative_discrete" and default_tabletype != "quantitative_continuous":
		print('Tabletype incorrect')
		return 

	projects = db['projects']
	projects.update({"name" : oldname}, {"$set" : {"name" : name, "access" : access,
		"description" : description, "default_tabletype": default_tabletype}})

	if oldname != name:
		query = db.collection_names(include_system_collections=False)
		for table in query:
			spl = table.split("-")
			if spl[0] == oldname and table not in tableBlacklist:
				newtablename = name + "-" + spl[1]
				db[table].rename(newtablename)

def updateTable(projectname, tablename, newtablename, newtabletype):
	if re.match('^\w+$', newtablename) is None:
		print('Only alphanumeric characters and underscores can be included in the table name.')
		return
	elif len(newtablename) > maximumlength:
		print('Maximum length of the table name is 50 characters.')
		return
	elif newtabletype != "qualitative" and newtabletype != "quantitative_discrete" and newtabletype != "quantitative_continuous":
		print('Tabletype incorrect')
		return 

	newtable = projectname + "-" + newtablename
	oldtable = projectname + "-" + tablename
	if newtablename != tablename:
		db[oldtable].rename(newtable)
		db[newtable].update({"type" : "description"}, {"$set" : {"tabletype" : newtabletype}})
	else:
		db[newtable].update({"type" : "description"}, {"$set" : {"tabletype" : newtabletype}})

def deleteTable(projectname, tablename):
	name = projectname + "-" + tablename
	if len(gettables(projectname)) == 1:
		db[name].drop()
		while(len(gettables(projectname)) == 0):
			createTable(projectname, "log", getTabletypeDefault(projectname))
	else:
		db[name].drop()

def chargeProject(project, amt):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	if projectfile is not None:
		free = projectfile['free_logs']
		#Take away from free logs if they still exist
		if free > 0:
			if amt >= free:
				amtToSub = free
				projects.update({"name" : project}, {"$inc":{"unpaid_logs" : amt - amtToSub}})
				return 0
			else:
				amtToSub = amt
				projects.update({"name" : project}, {"$inc":{"free_logs" : -amtToSub}})
				return free - amt
		else:
			projects.update({"name" : project}, {"$inc":{"unpaid_logs" : amt}})
			return 0
	else:
		return None

def checkProjectExists(name):
	projects = db['projects']
	if projects.find_one({"name" : name}) is None:
		#If project with that name doesn't exist, then return false.
		return False
	else:
		#Otherwise return true.
		return True

def log(project, table, value):
	name = project + "-" + table
	if db[name] is not None:
		log = {"type" : "log",
			   "value" : value,
			   "datetime" : int(time.time())}
		db[name].insert_one(log)
		projectlist = db['projects']
		projectlist.update({"name" : project}, {"$inc" : {"total_logs" : 1}})
	else:
		print('Cannot log because project or table name is not valid.')

def findlogs(project, table, amt):
	name = project + "-" + table
	coll = db[name]
	if coll is not None:
		content = []
		logs = coll.find().sort([("datecreated", pymongo.DESCENDING)]).limit(amt+1)
		for post in logs:
			if post['type'] == 'log':
				content.append(post['value'])
		return content
	else:
		return '404'

def getlogcount(project, table):
	name = project + "-" + table
	coll = db[name]
	if coll is not None:
		amt = coll.count()
		#Subtract one because one is a description not a log
		return amt - 1
	else:
		return '404'

#Get all of the table names in a project
def gettables(project):
	#Get all of the collections in the database
	query = db.collection_names(include_system_collections=False)
	results = []
	for table in query:
		if table.split("-")[0] == project and table not in tableBlacklist:
			#If the table starts with the project and
			#is not in the blacklist, add it to the returned list
			results.append(table)
	return results

def checkTableExists(project, table):
	query = db.collection_names(include_system_collections=False)
	name = project + "-" + table
	if name in query:
		return True
	else:
		return False

def getProjectFromKey(apikey):
	projects = db['projects']
	projectfile = projects.find_one({"secret_key" : apikey})
	if projectfile is None:
		return None
	else:
		return projectfile['name']

def getUserProjects(username):
	projects = db['projects']
	result = []
	for project in projects.find({"admins" : username}):
		result.append(project['name'])
	return result

def getProjectAccess(project):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	if projectfile is None:
		return None
	else:
		return projectfile['access']

def getProject(name):
	projects = db['projects']
	projectfile = projects.find_one({"name" : name})
	return projectfile

def getTabletype(projectname, tablename):
	name = projectname + "-" + tablename
	desc = db[name].find_one({"type" : "description"})
	return desc['tabletype']

def getTabletypeDefault(name):
	projects = db['projects']
	projectfile = projects.find_one({"name" : name})
	return projectfile['default_tabletype']

def getProjectStatus(project):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	return projectfile['status']

def resetKey(project):
	projects = db['projects']
	nkey = randKey(20)
	while(projects.find_one({"secret_key" : nkey})) is not None:
		nkey = randKey(20)

	projects.update({"name" : project}, {"$set" : {"secret_key" : nkey}})

def overallProjectSearch_withuser(query, username, amt):
	projects = db['projects']
	search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "access" : "public"}).sort([("popularity", pymongo.DESCENDING)]).limit(amt)
	personal_search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "admins" : username})

	#The search result changed to list form
	search2 = []
	#The final returned list (after compiling with private results)
	finalsearch = []
	for project in search:
		search2.append(project)

	search_names = []
	for post in search2:
		search_names.append(post['name'])

	for post in personal_search:
		if post['name'] not in search_names:
			finalsearch.append(post)

	for post in search2:
		finalsearch.append(post)

	return finalsearch

def overallProjectSearch(query, amt):
	projects = db['projects']
	search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "access" : "public"}).sort([("popularity", pymongo.DESCENDING)]).limit(amt)
	return search

def changeStatus(projectname, status):
	projects = db['projects']
	if status == "running" or status == "stopped" or status == "overdrawn":
		projects.update({"name" : projectname}, {"$set": {"status" : status}})

def likeProject(projectname):
	projects = db['projects']
	projects.update({"name" : projectname}, {"$inc" : {"popularity" : 1}})

def unlikeProject(projectname):
	projects = db['projects']
	projectfile = projects.find_one({"name" : projectname})
	if projectfile['popularity'] > 0:
		projects.update({"name" : projectname}, {"$inc" : {"popularity" : -1}})

def getFrequency_limit(projectname, tablename, limit):
	size = getlogcount(projectname, tablename)
	pipeline = [
		{"$group" : {"_id" : "$value", "count" : {"$sum" : 1}}},
		{"$sort" : SON([("count" , -1), ("_id", -1)])}
	]
	table = projectname + "-" + tablename
	result1 =  list(db[table].aggregate(pipeline))
	for entry in result1:
		if entry['_id'] is None:
			result1.remove(entry)
	final_results = []
	lm = 0
	total_so_far = 0
	for result in result1:
		if lm < limit:
			temp_dict = {}
			temp_dict['log'] = result['_id']
			temp_dict['count'] = result['count']
			final_results.append(temp_dict)
			total_so_far = total_so_far + result['count']
		else:
			#Compile everything else to the "others" category
			final_results.append({"Other" : (size - total_so_far)})
			break
		lm = lm + 1

	return final_results

def getFrequency(projectname, tablename):
	pipeline = [
		{"$group" : {"_id" : "$value", "count" : {"$sum" : 1}}},
		{"$sort" : SON([("count" , -1), ("_id", -1)])}
	]
	table = projectname + "-" + tablename
	first_list =  list(db[table].aggregate(pipeline))
	for entry in first_list: 
		if entry['_id'] is None:
			first_list.remove(entry)

def getTimeGraph(projectname, tablename, seconds):
	endtime = int(time.time()) - seconds
	pipeline = [
		{"$match" : { "datetime" : { "$gt" : endtime }}},
		{"$group" : {"_id" : "$value", "count" : {"$sum" : 1}}},
		{"$sort" : SON([("count" , -1), ("_id", -1)])},
	]
	table = projectname + "-" + tablename
	return list(db[table].aggregate(pipeline))

def getTimeGraph_alltime(projectname, tablename):
	pipeline = [
		{"$group" : {"_id" : "$datetime", "count" : {"$sum" : 1}}},
		{"$sort" : { "datetime" : 1 }},
	]
	table = projectname + "-" + tablename
	first_list = list(db[table].aggregate(pipeline))
	#Remove description:
	for entry1 in first_list:
		if entry1['_id'] is None:
			first_list.remove(entry1)

	#Float to activate acurate division
	first_time = db[table].find_one({"type" : "description"})['datecreated']
	total_time = int(time.time()) - first_time
	if total_time < 200:
		intervals = float(total_time)
	else:
		intervals = 200.0
	interval_list = []
	#For finding the best fits for existing log datetimes
	temp_list = []
	#Bad code
	if total_time < 1:
		set_int = 1.0/200
	else:
		set_int = total_time/intervals
	for i in range(int(intervals)):
		interval_list.append({"datetime" : (first_time + set_int*i), "count" : 0})
		temp_list.append(first_time + set_int*i)
	#Add the existing logs to the best fits in the empty sets
	for entry in first_list:
		closest = takeClosest(temp_list, entry['_id'])
		#Code requires optimization
		for p in interval_list:
			if p['datetime'] == closest:
				p['count'] = p['count'] + entry['count']
				break

	#Reduce the amount of datetimes in the x-axis labels
	counter = 0
	limit = 15
	#Get the type of the x axis by checking the earliest time's type 
	axis_listing = convertTime(total_time)[1]
	for entryb in interval_list:
		counter = counter + 1
		if counter % limit != 0 and counter != 1:
			interval_list[counter-1]['datetime'] = ""
		else:
			interval_list[counter-1]['datetime'] = round(convertTimeBased(float(int(time.time()) - entryb['datetime']), axis_listing), 1)
	return (interval_list, axis_listing)

def getHistogram(projectname, tablename):
	#Find the maximum and minimum values
	minpipeline = [
		{"$group" : {"_id" : "$type", "min" : {"$min" : "$value"}}},
	]
	maxpipeline = [
		{"$group" : {"_id" : "$type", "max" : {"$max" : "$value"}}},
	]
	table = projectname + "-" + tablename
	minimum = list(db[table].aggregate(minpipeline))
	maximum = list(db[table].aggregate(maxpipeline))
	if minimum[0]['_id'] == "log":
		min_final = float(minimum[0]['min'])
	elif minimum[1]['_id'] == "log":
		min_final = float(minimum[1]['min'])
	else:
		#Critical error
		return
	if maximum[0]['_id'] == "log":
		max_final = float(maximum[0]['max'])
	elif maximum[1]['_id'] == "log":
		max_final = float(maximum[1]['max'])
	else:
		#Critical error
		return
	
	#Divide into 10 equal segments
	count = getlogcount(projectname, tablename)
	if count < 10:
		intervals = int(count)
		interval = (max_final-min_final)/int(count)
	else:
		intervals = 10
		interval = (max_final-min_final)/10
	interval_list = []
	temp_list = []
	for i in range(int(intervals)):
		interval_list.append({"value" : round(min_final + interval*i, 1), "count" : 0})
		temp_list.append(round(min_final + interval*i, 1))

	#Add the existing logs to the best fits in the empty sets
	for entry in db[table].find({"type" : "log"}):
		closest = takeClosest(temp_list, float(entry['value']))
		#Code requires optimization
		for p in interval_list:
			if float(p['value']) == closest:
				p['count'] = str(int(p['count']) + 1)
				break

	#Make the values represent the ranges
	for q in interval_list:
		firstnumber = round(float(q['value']), 1)
		if int(firstnumber) == 0 or firstnumber/int(firstnumber) == 1.0:
			firstnumber = int(firstnumber)
		secondnumber = round(float(q['value']) + interval, 1)
		if int(firstnumber) == 0 or secondnumber/int(secondnumber) == 1.0:
			secondnumber = int(secondnumber)
		q['value'] = str(firstnumber) + " - " + str(secondnumber)

	return interval_list

#Credit: Lauritz V. Thaulow
def takeClosest(myList, myNumber):
    #Assumes myList is sorted. Returns closest value to myNumber.
    #If two numbers are equally close, return the smallest number.

    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

def convertTime(seconds):
	constant = 100
	if seconds < constant:
		return (seconds, "Seconds")
	elif seconds < constant * 60:
		return (seconds/60, "Minutes")
	elif seconds < constant * 3600:
		return (seconds/3600, "Hours")
	elif seconds < constant * 86400:
		return (seconds/86400, "Days")
	elif seconds < constant * 2626560:
		return (seconds/2626560, "Months")
	else:
		return (seconds/31518720, "Years")

def convertTimeBased(seconds, typ):
	if typ == "Seconds":
		return seconds
	elif typ == "Minutes":
		return seconds/60
	elif typ == "Hours":
		return seconds/3600
	elif typ == "Days":
		return seconds/86400
	elif typ == "Months":
		return seconds/2626560
	elif typ == "Years":
		return seconds/31518720
	print("CRITICAL ERROR")
