from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import requests
import MySQLdb
import xml.etree.ElementTree as ET
import xmltodict, json
import time

app = Flask(__name__)
api = Api(app)

agency = 'sf-muni'

db_hostname = 'mysql'
db_username = 'thousandEyes'
db_password = 'sup3rs3cr3t'
db_name = 'thousandEyes'

commands = {
    "agencyList": "http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList",
    "routeList": "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList",
    "routeConfig": "http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig",
    "predictions": "http://webservices.nextbus.com/service/publicXMLFeed?command=predictions",
    "predictionsForMultiStops": "http://webservices.nextbus.com/service/publicXMLFeed?command=predictionsForMultiStops",
    "schedule": "http://webservices.nextbus.com/service/publicXMLFeed?command=schedule",
    "messages": "http://webservices.nextbus.com/service/publicXMLFeed?command=messages",
    "vehicleLocations": "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations"
}

queries = {
    "selectAll": "SELECT * FROM statistics"
}

def convertToJson(xml):
    o = xmltodict.parse(xml)
    return o

def getUrl(url):
    req_time = time.time()
    response = requests.get(url)
    resp_time = time.time()
    return response

# Class for DB interactions
class Connection():
    def __init__(self):
        try:
            self.connection = MySQLdb.connect(host=db_hostname, user=db_username, passwd=db_password, db=db_name)
        except Exception as error:
            raise ValueError("Error! Unable to connect to the Database!")
    def selectQuery(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except:
            raise ValueError("Error! Unable to fetch data!")
    def dbDisconnect(self):
        try:
            self.connection.close()
        except:
            raise ValueError("Error! Unable to close the DB connection")

class DbWrapper():
    def __init__(self):
        self.conn = Connection()
    def selectQuery(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except:
            raise ValueError("Error! Unable to fetch data!")

class DbTest(Resource):
    def get(self):
        try:
            connection = DbWrapper()
            query = connection.selectQuery(queries['selectAll'])
            # connection.dbDisconnect()
        except ValueError as err:
            return err.args

        return query

class Test(Resource):
    def get(self):
        response = getUrl(commands['agencyList'])
        return convertToJson(response.content)

class RouteList(Resource):
    def get(self):
        response = requests.get(commands['routeList'] + "&a=" + agency)
        return convertToJson(response.content)


class DumpServices(Resource):
    def get(self):
        return commands

api.add_resource(DumpServices, '/dumpServices')
api.add_resource(DbTest, '/db')
api.add_resource(Test, '/test')
api.add_resource(RouteList, '/routes')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
