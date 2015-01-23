import math
import re
import sympy


nameHeader = 'Celestial Body (Reference code)'
parentHeader = 'Parent Body Reference Code'
smaHeader = 'Semimajor_axis'
periodHeader = 'Sidereal_period'
anomalyHeader = 'Mean_anomaly'
eccentricityHeader = 'Orbital_eccentricity'
ascendingNodeHeader = 'Longitude_of_the_ascending_node'
argumentPeriHeader = 'Argument_of_periapsis'

class Orbit:
	
	#Hohmann transfer time
	@classmethod
	def getTransferTime(cls, start, dest, mu):
		transferSma = 0.5*(start + dest)
		transferTime = math.pi * math.sqrt(math.pow(transferSma,3) / mu)
		return transferTime



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
		self.meanAnomaly = float(descr[anomalyHeader])
		self.ecc = float(descr[eccentricityHeader])
		self.ascendingNode = math.radians(float(descr[ascendingNodeHeader]))
		self.argumentOfPeriapsis = math.radians(float(descr[argumentPeriHeader]))
		self.parentMu = 4 * math.pow(math.pi, 2) * math.pow(self.sma, 3) / math.pow(self.period, 2)

	def __str__(self):
		ret = self.name + '\n'
		ret = ret + "SMA = %.0f km; Period = %.0f s; Ecc = %f" % (self.sma, self.period, self.ecc)
		return ret
	
	#Retrieve mean anomaly at given time (in seconds)
	def getMeanAnomaly(self, t):
		total = self.meanAnomaly + t*(2.0*math.pi/self.period)
		while total >= 2*math.pi:
			total-= 2*math.pi
		return total

	#Retrieve eccentric anomaly at given time with Kepler equation
	def getEccentricAnomaly(self, t):
		M = self.getMeanAnomaly(t)
		e = self.ecc
		E = sympy.Symbol('E')
		#The mean anomaly is a good approximation to start the numeric solver as long as eccentricity is small
		eccAnomaly = sympy.nsolve(E - e * sympy.sin(E) - M, E, M)
		return eccAnomaly
	
	def getTotalPhase(self,t):
		#Assume non eccentric and non inclined orbits
		return self.getMeanAnomaly(t) + self.ascendingNode + self.argumentOfPeriapsis

	def getTransferTimeTo(self, dest):
		return Orbit.getTransferTime(self.sma, dest.sma, self.parentMu)

	def getPhaseAngleForTransferTo(self, dest):
		return math.pi - (2*math.pi * self.getTransferTimeTo(dest) / dest.period)

	def getPhaseAngleWith(self, dest, t):
		a = self.getTotalPhase(t)
		b = dest.getTotalPhase(t)
		return (b-a)
	
	def getSynodicPeriod(self, dest):
		return (1.0/(1.0/dest.period - 1.0/self.period))

	
	def getHohmannOpportunityAfter(self, dest, t):
		currentAngle = self.getPhaseAngleWith(dest, t)
		desiredAngle = self.getPhaseAngleForTransferTo(dest)
		waitTime = (desiredAngle - currentAngle)/self.getSynodicPeriod(dest)
		return (t+waitTime)

		




