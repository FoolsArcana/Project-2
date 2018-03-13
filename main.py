import time
import atexit
import os
import csv
import requests
import json
import numpy
import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


listOfPrimeGeoLocs = []
allGeoLocsWeatherLocs = {}
allWeatherLocs = []
weatherEndpoint = "https://api.weather.gov/"


#do initialization tasks: setting and checking the locations (if necessary), prep the hourly web reqs, any additional web service needed.
def init():

	getLocs()
	
	initScheduler()
	
	
    app.run(debug=False)

def getLocs():
	
	#check config file
	if !os.path.exists("config.json"):
		#get initial core locations
		counter = 0
		stop = False
		while(!stop):
			initLat= input("latitude of location "+str(counter)+"? ('fin' to stop)")
			if(initLocation=='fin':
				stop = True
				break
			initLon = input("longitude of location "+str(counter)+"? (-180 < lon <= 180")
			doubleLat = -91
			doubleLon = -181
			try:
				doubleLat = float(initLat)
				doubleLon = float(initLon)
			except:
				print("error on input, values must be a valid float")
				continue
			if(doubleLat<90 && doubleLat > -90 && doubleLon>-180 && doubleLon<=180):
				listOfPrimeGeoLocs.append((doubleLon,doubleLat))
				counter++
			else:
				print("error on input, values must be within normal Earth range")
				continue
			
			counter+=1
		
		outputDict = {"primaryGeoLocations":listOfPrimeGeoLocs}
		try:
			with open('config.json', 'w') as configFileOut:
				json.dump(outputDict, configFileOut)
		
		except:
			print("error writing config file, now exiting")
			sys.exit(1)
	#load config file
	configData = {}	
	configChanged = False
	with open('config.json', 'r') as configFileIn:
		 configData = json.load(configFileIn)
	
	listOfPrimeGeoLocs = configData["primaryGeoLocations"]
	
	if(!("geoWeatherLocMap" in configData)):
		allGeoLocsWeatherLocs = getAllGeoWeatherLocMappings()
		configData["geoWeatherLocMap"]=allGeoLocsWeatherLocs
		configChanged = True
	else:
		allGeoLocsWeatherLocs = configData['geoWeatherLocMap']
	
	if(!("weatherLocs" in configData)):
		allWeatherLocs = numpy.unique(allGeoLocsWeatherLocs.values())
		configData["weatherLocs"]=allWeatherLocs
		configChanged = True
	else:
		allWeatherLocs = configData["weatherLocs"]
	#write to config file if any data changed
	if(configChanged):
		try:
			with open('config.json', 'w') as configFileOut:
				json.dump(configData, configFileOut)
		except:
			print("error modifying config file, now continuing")
			
	print("location initialization and update complete.")
	
	
#check api.weather.gov for the office and region for all the locations we gonna check.
def getAllGeoWEatherLocMappings():
	#get a resolution of full locations to 0.02 degrees spacing lat/lon, so approximate distance between points is ~ 0.15 mi (i.e. over a thousand feet)
	fullSet = [(2*round(loc[0]/2.0,2),2*round(loc[1]/2.0,2)) for loc in primaryGeoLocations]
	
	locSet = []
	retDict = {}
	
	highOffset = 0.1
	lowOffset = 0.4
	stepLow = 0.2
	stepHigh = 0.02
	for loc in fullSet:
		curLon = loc[0]
		curLat = loc[1]
		#pattern is +/-0.1 deg at 0.02 deg step (121 points), and +/- 0.4 deg at 0.2 step (24 points) for a total of 145 maximum points of interest / major location
		lonMinLow =  curLon-lowOffset
		lonMinHigh = curLon-highOffset
		lonMaxLow = curLon+lowOffset+stepLow
		lonMaxHigh =curLon + highOffset + stepHigh
		latMinLow =  curLat-lowOffset
		latMinHigh = curLat-highOffset
		latMaxLow = curLat+lowOffset+stepLow
		latMaxHigh =curLat + highOffset + stepHigh
		#high res
		for lon in range(lonMinHigh,lonMaxHigh, stepHigh):
			for lat in range(latMinHigh,latMaxHigh, stepHigh):
				locSet.append((lon,lat))
		
		for lon in range(lonMinLow,lonMaxLow, stepLow):
			for lat in range(latMinLow,latMaxLow, stepLow):
				locSet.append((lon,lat))
				
	locSet = numpy.unique(locSet)
	
	
	#the part where we call the weather api for its locations
	#'https://api.weather.gov/points/lat,lon
	for uniqueLocation in locSet:
		try:
			response = requests.get(weatherEndpoint+"points/"+str(uniqueLocation[1])+","+str(uniqueLocation[0]))
			properties = response.json()["properties"]
			valueAnswer =	(properties["cwa"],properties["gridX"],properties["gridY"])
			retDict[uniqueLocation]=valueAnswer
		except:
			continue
	return retDict
	
#init the scheduler for periodically checking weather.api.gov
def initScheduler():
	
	scheduler = BackgroundScheduler()
	scheduler.start()
	scheduler.add_job(
		func=checkWeather,
		trigger=IntervalTrigger(seconds=3600),
		id='weather_pull',
		name='Call Weather API every hour',
		replace_existing=True)
	# Shut down the scheduler when exiting the app
	atexit.register(lambda: scheduler.shutdown())
	
def checkWeather():
    #print time.strftime("%A, %d. %B %Y %I:%M:%S %p")
	hackTime = datetime.datetime.now()
	strTime = hackTime.strftime("%y_%m_%d_%H")
	for item in allWeatherLocs:
		office = item[0]
		gridX = item[1]
		gridY = item[2]
		dirPath = "/data/"+office+"/"+str(gridX)+"_"+str(gridY)
		if!(os.path.isdir(dirPath)):
			try:
				os.makedirs(dirPath)
			except Exception, e:
				print("Error: could not create required directory.")
				print(e)
				sys.exit(1)
			"""
			       "forecast": "https://api.weather.gov/gridpoints/IND/27,26/forecast",
        "forecastHourly": "https://api.weather.gov/gridpoints/IND/27,26/forecast/hourly",
        "forecastGridData": "https://api.weather.gov/gridpoints/IND/27,26",
        "observationStations": "https://api.weather.gov/gridpoints/IND/27,26/stations",
			"""
		writeBlob = {}
		#forecastGridData
		gridDataEndpoint = weatherEndpoint+"gridpoints/"+office+"/"+str(gridX)+","+str(gridY)
		#forecastHourly
		hourlyEndpoint = gridDataEndpoint +"/hourly"
		#forecast
		forecastEnpoint=gridDataEndpoint +"/forecast"
		#endpoint1:
			
			
		try:
			#the endpoints
			writeBlob["gridData"] = requests.get(gridDataEndpoint).json()
		except Exception, e:
			print("Warning: "+str(item)+" failed on grid data weather request.")
			print(e)
			time.sleep(5)
			continue
			
		try:
			#the endpoints
			writeBlob["hourlyData"] = requests.get(hourlyEndpoint).json()
		except Exception, e:
			print("Warning: "+str(item)+" failed on hourly forecast weather request.")
			print(e)
			time.sleep(5)
			continue
			
		try:
			#the endpoints
			writeBlob["forecastData"] = requests.get(forecastData).json()
		except Exception, e:
			print("Warning: "+str(item)+" failed on forecast weather request.")
			print(e)
			time.sleep(5)
			continue
		
		#write the data (later to be replaced with db access)
		try:
			with open(os.path.join(dirPath,strTime+'.json'), 'w') as curFileOut:
				json.dump(writeBlob, curFileOut)
		except:
			print("error writing data file "+ str(item)+", now exiting")
			continue

if __name__ == "__main__":
	main()









