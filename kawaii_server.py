from flask import Flask, jsonify
from werkzeug.routing import BaseConverter
import json
import pandas as pd
import numpy as np
import seaborn as sas
import matplotlib.pyplot as pyp
import sqlalchemy
import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy_utils import database_exists, create_database
Base = automap_base()
sas.set()


app = Flask("Led to Gold in a single vial")

	
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def timewarp(newdt=datetime.datetime.today()):
    now = newdt
    strnow = now.strftime('%Y-%m-%d')
    then = now-datetime.timedelta(weeks=52)
    strthen = then.strftime('%Y-%m-%d')
    return (strnow, strthen)
	
def lastTwelveMonths():
    retTuple = timewarp()
	return getTimeRangeQuery(retTuple)
	
def getTimeRangeQuery(dateTuple)
    q1 = session.query(measurements).filter(measurements.temp!=None)
    return q1.filter(and_(measurements.date<= dateTuple[0],measurements.date>=dateTuple[1]))
	


app.url_map.converters['regex'] = RegexConverter

@app.route('/api/v1.0/precipitation')
def fallForwards():
	queryAnswer = lastTwelveMonths()
	df1 = pd.read_sql(queryAnswer.statement,queryAnswer.session.bind)
	df1 = df1[['date','precip']]
	df1.set_index('date',inplace=True)
	return jsonify(df1.to_dict()['temp'])

@app.route('/api/v1.0/stations')
def ES():
	retList = [x[0] for x in session.query(stations.station_name)]
	return jsonify(retList)

@app.route('`/api/v1.0/tobs')
def freq():
	queryAnswer = lastTwelveMonths()
	df1 = pd.read_sql(queryAnswer.statement,queryAnswer.session.bind)
	df1 = df1[['date','precip']]
	df1.set_index('date',inplace=True)
	return jsonify(df1['temp'].tolist())


@app.route('/api/v1.0/<regex(".*"):uid>')
def dates(uid):
	strings = uid.split('/')
	str2 = strings[0]
	if len(strings)<=1:
		#we can't have data for a date that hasn't happened yet.
		str1=datetime.datetime.today().strftime('%Y-%m-%d')
	else:
		str1=strings[1]
	queryAnswer = getTimeRangeQuery((str1,str2))
	df1 = pd.read_sql(queryAnswer.statement,queryAnswer.session.bind)
	df1 = df1[['date','precip']]
	df1.set_index('date',inplace=True)
	tempSeries = df1['temp']
	return jsonify([tempSeries.min(),tempSeries.mean(),tempSeries.max()])
		

if __name__ == '__main__':
	engine = create_engine('sqlite:///resources/hawaii.sqlite')
	if not database_exists(engine.url):
		create_database(engine.url)
	conn = engine.connect()
	# Create the garbage_collection table within the database
	Base.prepare(engine,reflect=True)
	print(Base.classes.keys())
	# To push the objects made and query the server we use a Session object

	session = Session(bind=engine)
	measurements = Base.classes.measurements
	stations = Base.classes.stations
	
	app.run(debug=True)