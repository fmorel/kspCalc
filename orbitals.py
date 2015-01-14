#!/usr/bin/python
import math
import csv
import argparse
import sys
import re
import sympy

#---------------------------------------------
#CSV import 

nameHeader = 'Celestial Body (Reference code)'
parentHeader = 'Parent Body Reference Code'
smaHeader = 'Semimajor_axis'
periodHeader = 'Sidereal_period'
anomalyHeader = 'Mean_anomaly'
eccentricityHeader = 'Orbital_eccentricity'
ascendingNodeHeader = 'Longitude_of_the_ascending_node'

#Clean CSV data for practical use
def cleanPlanetParams(planet):
	planet[parentHeader] = int(planet[parentHeader])
	planet[smaHeader] = float(planet[smaHeader].replace(',',''))/1000
	planet[periodHeader] = float(planet[periodHeader].replace(',',''))
	planet[anomalyHeader] = float(planet[anomalyHeader])
	planet[eccentricityHeader] = float(planet[eccentricityHeader])
	return planet


#Fetch/Get a planet
def fetchPlanet(planetNameOrCode):
	for planet in planets:
		if planet[nameHeader].find(str(planetNameOrCode)) >= 0:
			return planet
	return None

def getCode(planet):
	m = re.search("\((?P<code>[0-9]+)\)",planet[nameHeader])
	return int(m.group('code'))


#------------------------------------------------
#Getter for physical orbitals parameter or values

#Retrieve gravitational parameter mu
def getOrbitalParameter(planet):
	sma = planet[smaHeader]
	period = planet[periodHeader]
	return 4 * math.pow(math.pi, 2) * math.pow(sma, 3) / math.pow(period, 2)

#Retrieve mean anomaly at given time (in seconds)
def getMeanAnomaly(planet, t):
	total = planet[anomalyHeader] + t*(2.0*math.pi/planet[periodHeader])
	while total >= 2*math.pi:
		total-= 2*math.pi
	return total

#Retrieve eccentric anomaly at given time with Kepler equation
def getEccentricAnomaly(planet, t):
	M = getMeanAnomaly(planet, t)
	e = planet[eccentricityHeader]
	E = sympy.Symbol('E')
	#The mean anomaly is a good approximation to start the numeric solver as long as eccentricity is small
	eccAnomaly = sympy.nsolve(E - e * sympy.sin(E) - M, E, M)
	return eccAnomaly

		
#----------------------------------------------
#Main code

#Open csv data retrieved from http://wiki.kerbalspaceprogram.com/wiki/Celestials
csvFile = open('orbitals.csv', 'r')
csvDict = csv.DictReader(csvFile)

#Create planets dictionnary
planets = []
for row in csvDict :
	planets.append(row)
csvFile.close()
del planets[0]

#Clean CSV output
planets = map (cleanPlanetParams, planets)

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("start", help="Starting celestial body")
parser.add_argument("dest", help="Destination body")
parser.add_argument("-s", "--startRadius", help="Current radius of spacecraft orbit in kilometers")
parser.add_argument("-d", "--destRadius", help="Radius of destination when orbit is eccentric ...")
parser.add_argument("-i", "--info", help="Display information of mentionned planet")
parser.add_argument("-t", "--time", help="Current time in game, in seconds")
args = parser.parse_args()


planetToSatellite = False

#Print info/debug
if args.info :
	planet = fetchPlanet(args.info)
	print planet
	T=float(planet[periodHeader])
	if args.time:
		T=float(args.time)
	print "After T=", T
	print "Mean anomaly is ", math.degrees(getMeanAnomaly(planet, T))
	print "Eccentric anomaly is ", math.degrees(getEccentricAnomaly(planet, T))
	sys.exit()


#For now the default behavious is a static Hohman transfer calculator

startPlanet = fetchPlanet(args.start)
destPlanet = fetchPlanet(args.dest)

#Detect error cases
if startPlanet is None  or destPlanet is None:
	print "Planets not found"
	sys.exit()

if int(destPlanet[parentHeader]) != getCode(startPlanet) and destPlanet[parentHeader] != startPlanet[parentHeader]:
	print "Incompatible orbiting characteristics of bodies"
	sys.exit()

if destPlanet[parentHeader] == getCode(startPlanet) :
	planetToSatellite = True
	if args.startRadius is None :
		print "Destination body orbits around Starting body, I need radius of current orbit"
		sys.exit()
	else : 
		radius = args.startRadius
else :
	if args.startRadius is None :
		radius = startPlanet[smaHeader]
	else :
		radius =args.startRadius

#Simple Kerpler's law to determine the travel time of the Hoffman transfer orbit
radius = float(radius)

if args.destRadius is None :
	destSma = destPlanet[smaHeader]
else :
	destSma = float(args.destRadius)

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

print "Destination planet will travel ", angle, " degrees while transfer orbit"
print "Destination planet should be ", phi, "d egrees ahead from spacecraft at injection"
print "Transfer time is ", transferTime, " seconds"
print "Lambda is ", math.degrees(lambd), "degrees from the spacecraft/parent body line"
print "Inital delta-V for Hoffman transfer is", dV1, "m/s"
print "Final delta-V for capture is", dV2, "m/s"



