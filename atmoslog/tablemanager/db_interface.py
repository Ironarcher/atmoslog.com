import random
import time
from pymongo import MongoClient

c = MongoClient('localhost', 27017)
db = c['atmos_final']

def randKey(digits):
	return ''.join(random.choice(
		'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(digits))

def createTable(ownerproject, tablename):
	projects = db['projects']
	projectfile = projects.find_one({"name" : onwerproject})
	if projectfile is not None:
		name = ownerproject.join('-').join(tablename)
		if db[name] is None:
			db.createCollection(name)
			description = {"type:" : "description",
						   "duplicate_loss" : 0,
						   "incorrect_syntax" : 0,
						   "invalid_table_name" : 0,
						   "packet_too_large" : 0,
						   "invalid_api_key" : 0
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
def createProject(name, creator, access):
	projects = db['projects']
	key = randKey(20)
	while(projects.find_one({"secret_key" : key})) is not None:
		key = randKey(20)

	if projects.find_one({"name" : name}) is None:
		description = {"name" : name,
					   "tables" : ['logs'],
					   "admins" : [creator],
					   "contributors" : [creator],
					   "readers" : [creator],
					   "access" : access,
					   "secret_key" : key}
		projects.insert_one(description)
	else:
		print("Error: Project name already exists. Choose a different name.")

def log(project, table, value):
	name = ownerproject.join('-').join(tablename)
	if db[name] is not None:
		log = {"type" : "log",
			   "value" : value,
			   "dateCreated" : int(time.time())}
	else:
		print('Cannot log because project or table name is not valid.')

def findlogs(project, table, amt):
	name = ownerproject.join('-').join(tablename)
	coll = db[name]
	if coll is not None:
		content = {}
		counter = 0
		for post in coll.find():
			if counter < amt:
				content.append(post[value])
				counter = counter + 1
			else:
				break
	else:
		return '404'