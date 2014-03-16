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

#Retrieve gravitational parameter mu
def getOrbitalParameter(planet):
	sma = planet[smaHeader]
	period = planet[periodHeader]
	return 4 * math.pow(math.pi, 2) * math.pow(sma, 3) / math.pow(period, 2)

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

#Simple Kerpler's law to determine the travel time of the Hoffman transfer orbit
radius = float(radius)
destSma = destPlanet[smaHeader]
transferSma = 0.5*(radius + destSma)
mu = getOrbitalParameter(destPlanet)
transferTime = math.pi * math.sqrt(math.pow(transferSma,3) / mu)
angle = 360 * (transferTime / destPlanet[periodHeader])

#Following calculus to retrieve 'navball angle' lambda was found here :
#https://docs.google.com/document/d/1IX6ykVb0xifBrB4BRFDpqPO6kjYiLvOcEo3zwmZL0sQ/edit?pli=1
phi = 180-angle
d = math.sqrt(pow(radius,2) + pow(destSma, 2) - 2*radius*destSma*math.cos(math.radians(phi)))
lambd = math.asin(destSma/d*math.sin(math.radians(phi)))


#Delta-v computing
dV1 = math.sqrt(mu/radius) * (math.sqrt(destSma/transferSma) -1)*1000
dV2 = math.sqrt(mu/destSma) * (1 - math.sqrt(radius/transferSma))*1000

print "Destination planet will travel ", angle, "degrees while transfer orbit"
print "Destination planet should be ", phi, "degrees ahead from spacecraft at injection"
print "Lambda is ", math.degrees(lambd), "degrees from the spacecraft/parent body line"
print "Inital delta-V for Hoffman transfer is", dV1, "m/s"
print "Final delta-V for capture is", dV2, "m/s"



