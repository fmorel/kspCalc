import math
import re


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
	#Time constant in KSP universe
	MINUTES = 60
	HOURS = 60 * MINUTES
	DAYS = 6 * HOURS
	YEARS = 426 * DAYS

	def __init__(self, seconds):
		self.total = seconds
		self.compute()
	
	@classmethod
	def parse(cls, string):
		m = re.search("^(?P<years>\d*):(?P<days>\d*)", string)
		if m :
			years = int(m.group('years'))-1
			days = int(m.group('days'))-1
			total = years* Time.YEARS + days * Time.DAYS
			return cls(total)
		return None

	def __str__(self):
		return "Y %d, D %d, %d:%d:%d" % (self.years, self.days, self.hours, self.minutes, self.seconds)

	def compute(self):
		total = self.total
		self.years = total // Time.YEARS
		total -= self.years * Time.YEARS
		self.days = total // Time.DAYS
		total -= self.days * Time.DAYS
		self.hours = total // Time.HOURS
		total -= self.hours * Time.HOURS
		self.minutes = total // Time.MINUTES
		total -= self.minutes * Time.MINUTES
		self.seconds = total
		#Time 0 corresponds to year 1, day 1 :
		self.years += 1
		self.days += 1

	def add(self, seconds):
		self.total += seconds
		self.compute()



