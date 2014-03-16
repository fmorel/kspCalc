#!/usr/bin/python
import math
import csv
import argparse
import sys
import re

nameHeader = 'Celestial Body (Reference code)'
parentHeader = 'Parent Body Reference Code'
smaHeader = 'Semimajor_axis'
periodHeader = 'Sidereal_period'

#Helper functions
def fetchPlanet(planetNameOrCode):
	for planet in planets:
		if planet[nameHeader].find(str(planetNameOrCode)) >= 0:
			return planet
	return None

def getCode(planet):
	m = re.search("\((?P<code>[0-9]+)\)",planet[nameHeader])
	return int(m.group('code'))

def getOrbitalParameter(planet):
	sma = planet[smaHeader]
	period = planet[periodHeader]
	return (period*period) / (sma*sma*sma)

def changePlanetParams(planet):
	planet[parentHeader] = int(planet[parentHeader])
	planet[smaHeader] = float(planet[smaHeader].replace(',',''))/1000
	planet[periodHeader] = float(planet[periodHeader].replace(',',''))
	return planet

		

#Open csv data retrieved from http://wiki.kerbalspaceprogram.com/wiki/Celestials
csvFile = open('orbitals.csv', 'r')
csvDict = csv.DictReader(csvFile)

#Create planets dictionnary
planets = []
for row in csvDict :
	planets.append(row)
csvFile.close()
del planets[0]

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("start", help="Starting celestial body")
parser.add_argument("dest", help="Destination body")
parser.add_argument("-a", "--altitude", help="Current radius of spacecraft orbit in kilometers")
args = parser.parse_args()

startPlanet = fetchPlanet(args.start)
destPlanet = fetchPlanet(args.dest)

#Change parant field so it is an integer
planets = map (changePlanetParams, planets)
planetToSatellite = False

#Detect error cases
if startPlanet is None  or destPlanet is None:
	print "Planets not found"
	sys.exit()

if int(destPlanet[parentHeader]) != getCode(startPlanet) and destPlanet[parentHeader] != startPlanet[parentHeader]:
	print "Incompatible orbiting characteristics of bodies"
	sys.exit()

if destPlanet[parentHeader] == getCode(startPlanet) :
	planetToSatellite = True
	if args.altitude is None :
		print "Destination body orbits around Starting body, I need radius of current orbit"
		sys.exit()
	else : 
		radius = args.altitude
else :
	if args.altitude is None :
		radius = startPlanet[smaHeader]
	else :
		radius =args.altitude

radius = float(radius)	
transferSma = 0.5*(radius + destPlanet[smaHeader])
transferTime = 0.5*math.sqrt(math.pow(transferSma,3) * getOrbitalParameter(destPlanet))

print "Destination planet will travel ", 360 * (transferTime / destPlanet[periodHeader]), "degrees while transfer orbit"



