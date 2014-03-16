#!/usr/bin/python

import csv
import argparse
import sys
import re

nameHeader = 'Celestial Body (Reference code)'
refHeader = 'Parent Body Reference Code'

#Helper functions
def fetchPlanet(planetNameOrCode):
	for planet in planets:
		if planet[nameHeader].find(planetNameOrCode) >= 0:
			return planet
	return None

def getCode(planet):
	m = re.search("\((?P<code>[0-9]+)\)",planet[nameHeader])
	return int(m.group('code'))



#Open csv data retrieved from http://wiki.kerbalspaceprogram.com/wiki/Celestials
csvFile = open('orbitals.csv', 'r')
csvDict = csv.DictReader(csvFile)

#Create planets dictionnary
planets = []
for row in csvDict :
	planets.append(row)
csvFile.close()

print planets[2]
#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("start", help="Starting celestial body")
parser.add_argument("dest", help="Destination body")
parser.add_argument("-a", "--altitude", help="Current radius of spacecraft orbit")
args = parser.parse_args()

startPlanet = fetchPlanet(args.start)
destPlanet = fetchPlanet(args.dest)

if startPlanet is None  or destPlanet is None:
	print "Planets not found"
	sys.exit();

if int(destPlanet[refHeader]) == getCode(startPlanet) and args.altitude is None:
	print "Destination body orbits around Starting body, I need altitude of current orbit"
	sys.exit();



#headers = csvData[0]
#print "Header length is : ",len(headers)
#for row in csvData[2:] :
#	planet={}
#	print "Row length is : ",len(row)
#	for j,cell in enumerate(row) :
#		if j < len(headers) and headers[j] != '':
#			planet[headers[j]] = cell
#	planets.append(planet)

#print planets[0]

