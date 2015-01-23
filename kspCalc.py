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


#Parse arguments
parser = argparse.ArgumentParser()
#parser.add_argument("start", help="Starting celestial body")
#parser.add_argument("dest", help="Destination body")
parser.add_argument("-s", "--startRadius", help="Current radius of spacecraft orbit in kilometers")
parser.add_argument("-d", "--destRadius", help="Radius of destination when orbit is eccentric ...")
parser.add_argument("-i", "--info", help="Display information of mentionned planet")
parser.add_argument("-t", "--time", help="Current time in game, in seconds")
args = parser.parse_args()



#Print info/debug
if args.info :
	planet = filter(lambda b : b.name == args.info, planets)[0]
	print planet
	T=planet.period
	if args.time:
		T=float(args.time)
	print "After T=", T
	print "Mean anomaly is ", math.degrees(planet.getMeanAnomaly(T))
	print "Eccentric anomaly is ", math.degrees(planet.getEccentricAnomaly(T))
	sys.exit()





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



