from bottle import route, run, request
from pymongo import MongoClient
import json
import MySQLdb
import datetime
from bson import json_util
import pytz

client = MongoClient('localhost', 27017)
mongoDB = client.pydb
shirtCol = mongoDB.shirts


db = MySQLdb.connect(host="localhost", # your host, usually localhost
					user="root", # your username
					passwd="summer", # your password
					db="pydb") # name of the data base
cursor = db.cursor()

def connectMySql():
	global db
	db = MySQLdb.connect(host="localhost", # your host, usually localhost
					user="root", # your username
					passwd="summer", # your password
					db="pydb")
	global cursor 
	cursor = db.cursor()
	print "connection established"
	#return cursor
	

timezone = 'America/Los_Angeles'
localFormat = "%Y-%m-%d %H:%M:%S"

@route('/shirt/<shirtID>', method='GET')
def getShirt( shirtID=1234 ):
	doc = shirtCol.find_one({"shirtId":shirtID},{"_id":0})
	if not doc:
		return {"error":"No shirt found"}
	#doc['createdDate'] = doc['createdDate'].strftime("%Y-%m-%d")
	return doc
	#return json.dumps(doc, default=json_util.default)

@route('/shirts', method="PUT")
def updateShirt():
	doc = request.json
	print "doc is %s" % doc
	olddoc = shirtCol.find_one({"shirtId":doc['shirtId']},{"_id":0})
	doc['createdDate'] = olddoc['createdDate']
	shirtCol.update({"shirtId": doc['shirtId']}, doc)
	return { "success" : True}

@route('/shirts', method='DELETE' )
def deleteShirts():
	doc = request.json
	shirtCol.remove({"shirtId" : doc['shirtId']})
	return { "success" : "OK"}

@route('/shirts', method='POST')
def insertShirt():
	
	#print "inside post"
	doc = request.json
	currentMoment = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
	localDatetime = currentMoment.astimezone(pytz.timezone(timezone))
	doc['createdDate'] = localDatetime.strftime(localFormat)
	print "doc is %s" % doc
	id = shirtCol.insert(doc)
	return { "success" : "OK" }

@route('/shoe/<shoeId>', method='GET')
def getShoe(shoeId="1"):
	
	try:
		cursor.execute("SELECT shoeId, shoeName, shoeQuantity, createdBy, createdDate FROM SHOE_TABLE where shoeId = %s" % shoeId)
	except (AttributeError, MySQLdb.OperationalError):
		print "inside exception"
		connectMySql()
		cursor.execute("SELECT shoeId, shoeName, shoeQuantity, createdBy, createdDate FROM SHOE_TABLE where shoeId = %s" % shoeId)
	
	row = cursor.fetchone()
	if not row:
		return {"error": "no shoe found"}
	return {"shoeId": row[0], "shoeName": row[1], "shoeQuantity": row[2], "createdBy": row[3], "createdDate": row[4]}

@route('/shoes', method="PUT")
def updateShoe():
	shoe = request.json
	sql = "Update SHOE_TABLE set shoeName = '%s', createdBy = '%s', shoeQuantity = '%s' where shoeId = '%s'" % (shoe['shoeName'],shoe['createdBy'], shoe['shoeQuantity'], shoe['shoeId'])
	#sql = "Update SHOE_TABLE set shoeName = %s ,createdBy = %s shoeQuantity = %s where shoeId = %s" % (shoe['shoeName'],shoe['createdBy'], shoe['shoeQuantity'], shoe['shoeId'])
	#print sql
	try:
		cursor.execute(sql)
	except (AttributeError, MySQLdb.OperationalError):
		connectMySql()
		cursor.execute(sql)
	db.commit()
	return { "success" : "OK"}

@route('/shoes', method='DELETE' )
def deleteShoe():
	doc = request.json
	try:
		cursor.execute("DELETE From SHOE_TABLE where shoeId= %s" %doc['shoeId'])
	except (AttributeError, MySQLdb.OperationalError):
		connectMySql()
		cursor.execute("DELETE From SHOE_TABLE where shoeId= %s" %doc['shoeId'])
	return { "success" : "OK"}

@route('/shoes', method='POST')
def insertShoe():
	
	doc = request.json
	currentMoment = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
	localDatetime = currentMoment.astimezone(pytz.timezone(timezone))
	doc['createdDate'] = localDatetime.strftime(localFormat)
	query = "Insert into SHOE_TABLE (shoeId, shoeName, shoeQuantity, createdBy, createdDate) values (%s, %s, %s, %s, %s)"

	try:
		cursor.execute(query, (doc['shoeId'], doc['shoeName'], doc['shoeQuantity'], doc['createdBy'], doc['createdDate']))	
	except (AttributeError, MySQLdb.OperationalError):
		connectMySql()
		cursor.execute(query, (doc['shoeId'], doc['shoeName'], doc['shoeQuantity'], doc['createdBy'], doc['createdDate']))
		
	db.commit()
	return { "success" : "OK" }

if __name__ == "__main__":
	run(host='0.0.0.0', port=8080)
	
