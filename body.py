import math
import re

from utils import *

nameHeader = 'Celestial Body (Reference code)'
parentHeader = 'Parent Body Reference Code'
smaHeader = 'Semimajor_axis'
periodHeader = 'Sidereal_period'
anomalyHeader = 'Mean_anomaly'
eccentricityHeader = 'Orbital_eccentricity'
ascendingNodeHeader = 'Longitude_of_the_ascending_node'
argumentPeriHeader = 'Argument_of_periapsis'

class Body:
	def __init__(self, descr):
		#Separate Name/Code
		m = re.search("(?P<name>\w+).*\((?P<code>[0-9]+)\)", descr[nameHeader])
		self.name = m.group('name')
		self.code = int(m.group('code'))
		#Fetch other values easily
		self.parent = int(descr[parentHeader])
		self.sma = float(descr[smaHeader].replace(',',''))/1000
		self.period = float(descr[periodHeader].replace(',',''))
		#meanAnomaly already given in radians
		self.meanAnomaly = float(descr[anomalyHeader]) 
		self.ecc = float(descr[eccentricityHeader])
		self.ascendingNode = math.radians(float(descr[ascendingNodeHeader]))
		self.argumentOfPeriapsis = math.radians(float(descr[argumentPeriHeader]))
		self.parentMu = 4 * math.pow(math.pi, 2) * math.pow(self.sma, 3) / math.pow(self.period, 2)

	def __str__(self):
		ret = self.name + '\n'
		ret = ret + "SMA = %.0f km; Period = %.0f s; Ecc = %f" % (self.sma, self.period, self.ecc) + '\n'
		ret = ret + "M = %.0f deg ; Asc Node = %.0f ; Arg Periapsis = %.0f" %(math.degrees(self.meanAnomaly), math.degrees(self.ascendingNode), math.degrees(self.argumentOfPeriapsis))
		return ret
	
	#Retrieve mean anomaly at given time (in seconds)
	def getMeanAnomaly(self, t):
		total = self.meanAnomaly + t*(2.0*math.pi/self.period)
		return Utility.clipAngle(total)

	def getTrueAnomaly(self, t):
		M = self.getMeanAnomaly(t)
		e = self.ecc
		ecube = e*e*e
		#Series expansion of true anomaly,found here : http://www.jgiesen.de/kepler/kepler1.html
		#We go up to  the fourth order in e, sufficient for e up to 0.2. Accuracy still acceptable (1deg error) for e up to 0.5
		return (M + (2*e - 0.25*ecube) * math.sin(M) + (1.25*e*e -(11/24)*ecube*e) * math.sin(2.0*M) + (13/12)*ecube * math.sin(3*M))

	def getRadius(self, nu):
		e = self.ecc
		radius = self.sma * (1 - e*e) / (1 + e*math.cos(nu))
		return radius
		
	def getTotalPhase(self,t):
		#Assume non eccentric and non inclined orbits
		#return self.getTrueAnomaly(t) + self.ascendingNode + self.argumentOfPeriapsis
		return self.getMeanAnomaly(t) + self.ascendingNode + self.argumentOfPeriapsis

	def getTransferTimeTo(self, dest):
		return Utility.getTransferTime(self.sma, dest.sma, self.parentMu)

	def getPhaseAngleForTransferTo(self, dest):
		return math.pi - (2*math.pi * self.getTransferTimeTo(dest) / dest.period)

	def getPhaseAngleWith(self, dest, t):
		a = self.getTotalPhase(t)
		b = dest.getTotalPhase(t)
		return (b-a)

	#Synodic period, positive when destination period is smaller (i.e phase angle is increasing with time)
	def getSynodicPeriod(self, dest):
		return (1.0/(1.0/dest.period - 1.0/self.period))

	#Compute the opportunity for perfect circular orbits
	def getHohmannOpportunityAfter(self, dest, t):
		currentAngle = self.getPhaseAngleWith(dest, t)
		desiredAngle = self.getPhaseAngleForTransferTo(dest)
		#First normalize travel angle between [0, 2*pi[
		travelAngle = Utility.clipAngle(desiredAngle - currentAngle)
		#Algebric Angular velocity of phase between the two bodies
		synodic = (self.getSynodicPeriod(dest) / (2*math.pi))
		#WaitTime is alwas positive so we take the angular value with the same sign as synodic velocity
		if synodic > 0:
			waitTime = travelAngle * synodic
		else:
			waitTime = (travelAngle - 2*math.pi) * synodic
		
		return (t+waitTime)
	
	def getHohmannOpportunityAccurate(self, dest, t):
		#First guess  is the circular opportunity
		estim = self.getHohmannOpportunityAfter(dest, t)
		loop=0
		while True :
			#Compute the exact position of bodies at estimate
			nus = self.getTrueAnomaly(estim)
			rs = self.getRadius(nus)
			#For destination body, add 180 deg because it is the destination of Hohmann tranfer
			nud = nus + self.ascendingNode + self.argumentOfPeriapsis +  math.pi \
				  - dest.ascendingNode - dest.argumentOfPeriapsis 
			rd = dest.getRadius(nud)
			
			#Compute the exact position of destination body after transfer and compare :
			#If it is ahead, diff is negative

			transferTime = Utility.getTransferTime(rs, rd, self.parentMu)
			diff = nud - dest.getTrueAnomaly(estim + transferTime)
			#Better choose algebric angles here
			diff = Utility.clipAngle(diff)
			if (diff > math.pi):
				diff -= 2*math.pi
			#And the correction depends if target planet is in inferior conjunction	
			sign = math.copysign(1, self.getSynodicPeriod(dest))
			#estim += math.copysign(diff / (2*math.pi) * self.period, syn)
			estim += sign * diff / (2*math.pi) * min(self.period , dest.period)

			loop += 1
			print math.degrees(diff)
			if (math.fabs(math.degrees(diff))<0.25) or (loop >= 10):
				break

		return estim


