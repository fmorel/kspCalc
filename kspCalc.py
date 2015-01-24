#!/usr/bin/python
import math
import csv
import argparse
import sys

from body import *
		
#----------------------------------------------
#Main code

#Open csv data retrieved from http://wiki.kerbalspaceprogram.com/wiki/Celestials
csvFile = open('orbitals.csv', 'r')
csvDict = csv.DictReader(csvFile)

#Create planets array
#We need to discard the first row, so ugly workaround with index ...
planets = []
idx = 0
for row in csvDict :
	if idx :
		planets.append(Body(row))
	idx += 1
csvFile.close()

#Easy accessor to a planet object with name
def fetchBody(name) :
	planet = filter(lambda b : b.name == name, planets)
	if planet :
		return planet[0]
	else :
		return  None


#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("start", help="Starting celestial body")
parser.add_argument("-s", "--startRadius", help="Current radius of spacecraft orbit in kilometers or body name. -d option is mandatory.")
parser.add_argument("-d", "--destRadius", help="Wanted radius of spacecraft or body name. -s option is mandatory.")
parser.add_argument("-p", "--planetary", help="Compute interplanetary path from start to mentionned planet. Incompatible with -s and -d")
parser.add_argument("-i", "--info", help="Display information of planet", action="store_true")
parser.add_argument("-t", "--time", help="Current time in game, in seconds")
args = parser.parse_args()


#Fetch the main planet
planet = fetchBody(args.start)
if not planet:
	print "Could not find planet " + args.start
	sys.exit() 

#Print info/debug
if args.info :
	print planet
	T=planet.period
	if args.time:
		T=int(args.time)
	T = Time(T)
	print "After T=", T
	print "Mean anomaly is ", math.degrees(planet.getMeanAnomaly(T.total))
	print "Eccentric anomaly is ", math.degrees(planet.getEccentricAnomaly(T.total))
	sys.exit()

#Check argument validity
if args.startRadius != args.destRadius :
	print "-s option only works with a corresponding -d"
	sys.exit()

#Handle orbit transfer around the same body 
if args.startRadius:
	print "Not supported for now"
	sys.exit()

#Handle interplanetary transfers
if args.planetary:
	dest = fetchBody(args.planetary)
	if not dest:
		print "Could not find planet " + args.planetary
	angle = planet.getPhaseAngleForTransferTo(dest)	
	print "Angle phase from %s to %s is %.1f degrees" % (planet.name, dest.name, math.degrees(angle))
	if args.time:
		T = Time.parse(args.time)
		if not T :
			T=int(args.time)
		else:
			T = T.total
		print "Current phase angle is %.1f degrees" % math.degrees(Utility.clipAngle(planet.getPhaseAngleWith(dest, T)))
		print "Next Hohmann opportunity (quick) is at "  + str(Time(planet.getHohmannOpportunityAfter(dest, T)))

	
	

##Following calculus to retrieve 'navball angle' lambda was found here :
##https://docs.google.com/document/d/1IX6ykVb0xifBrB4BRFDpqPO6kjYiLvOcEo3zwmZL0sQ/edit?pli=1
#phi = 180-angle
#d = math.sqrt(pow(radius,2) + pow(destSma, 2) - 2*radius*destSma*math.cos(math.radians(phi)))
#lambd = math.asin(destSma/d*math.sin(math.radians(phi)))
#
#
##Delta-v computing
#
##dV1 = math.sqrt(mu/radius) * (math.sqrt(destSma/transferSma) -1)*1000
##dV2 = math.sqrt(mu/destSma) * (1 - math.sqrt(radius/transferSma))*1000
#
#print "Destination planet will travel ", angle, " degrees while transfer orbit"
#print "Destination planet should be ", phi, "d egrees ahead from spacecraft at injection"
#print "Transfer time is ", transferTime, " seconds"
#print "Lambda is ", math.degrees(lambd), "degrees from the spacecraft/parent body line"



