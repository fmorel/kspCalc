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

class Utility:
	
	#Hohmann transfer time
	@classmethod
	def getTransferTime(cls, start, dest, mu):
		transferSma = 0.5*(start + dest)
		transferTime = math.pi * math.sqrt(math.pow(transferSma,3) / mu)
		return transferTime

	@classmethod
	def clipAngle(cls, angle):
		while angle < 0:
			angle += 2*math.pi
		while angle >= 2*math.pi:
			angle -= 2*math.pi
		return angle
	

class Time:
	def __init__(self, seconds):
		self.total = seconds
		self.compute()
	
	@classmethod
	def parse(cls, string):
		m = re.search("^(?P<years>\d*):(?P<days>\d*)", string)
		if m :
			years = int(m.group('years'))-1
			days = int(m.group('days'))-1
			total = (years*426 + days) * 3600 * 6
			return cls(total)
		return None

	def __str__(self):
		return "Y %d, D %d, %d:%d:%d" % (self.years, self.days, self.hours, self.minutes, self.seconds)

	def compute(self):
		#6 hours days, 426 days per year
		total = self.total
		self.years = total // (3600 * 6 * 426)
		total -= self.years * (3600 * 6 * 426)
		self.days = total // (3600*6)
		total -= self.days * (3600*6)
		self.hours = total // 3600
		total -= self.hours*3600
		self.minutes = total //60
		total -= self.minutes*60
		self.seconds = total
		#Time 0 corresponds to year 1, day 1 :
		self.years += 1
		self.days += 1

	def add(self, seconds):
		self.total += seconds
		self.compute()


	

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

	#Retrieve eccentric anomaly at given time with Kepler equation
	def getEccentricAnomaly(self, t):
		M = self.getMeanAnomaly(t)
		e = self.ecc
		E = sympy.Symbol('E')
		#The mean anomaly is a good approximation to start the numeric solver as long as eccentricity is small
		eccAnomaly = sympy.nsolve(E - e * sympy.sin(E) - M, E, M)
		return eccAnomaly

	def getTrueAnomalyApprox(self, t):
		M = self.getMeanAnomaly(t)
		e = self.ecc
		return (M + 2*e*math.sin(M) + 1.25*e*e*math.sin(2.0*M))
	
	def getTotalPhase(self,t):
		#Assume non eccentric and non inclined orbits
		#return self.getTrueAnomalyApprox(t) + self.ascendingNode + self.argumentOfPeriapsis
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

		




