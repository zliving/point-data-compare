import csv
from collections import OrderedDict
import pprint
from difflib import SequenceMatcher
from os import listdir
from os.path import isfile, join
import time
from operator import itemgetter

class ComparePointToReportData():

	pointDataFile = ''
	pointDataFolder = ''
	reportList = []
	keyFieldValue = None
	headers = 'field id, field name, database data, report data'

	def setDataFolder(self, folderName):
		self.pointDataFolder = folderName

	def setPointDataFile(self, fileName):
		self.pointDataFile = fileName

	def RepresentsInt(self, s):
		try:
			int(s)
			return True
		except ValueError:
			return False

	def readFilesFromFolder(self):
		self.reportList = [self.pointDataFolder+'/'+f for f in listdir(self.pointDataFolder) if isfile(join(self.pointDataFolder, f))]
		self.reportList.remove(self.pointDataFolder+'/.DS_Store')


	def compareAll(self):
		self.readFilesFromFolder()
		self.keyFieldValue = self.readFieldKeysFile('/Users/l-z-livingston/Downloads/FieldID_test.csv')
		orderedReportData, orderedPointData = self.getAllReportData(), self.readFieldFile(self.pointDataFile)
		self.getMissingPointData(orderedReportData, orderedPointData)
		self.comparePointAndReportData(orderedReportData, orderedPointData)

	def getAllReportData(self):
		reportDataList = OrderedDict()
		for report in self.reportList:
			reportDataList = self.merge_two_dicts(reportDataList, self.readFieldFile(report))

		return  OrderedDict(sorted(reportDataList.iteritems(), key=lambda x: x[0]))

	def similar(self,a,b):
		return SequenceMatcher(None, a, b).ratio()

	def readFieldFile(self,fileName):
		# Open the CSV file and process it line by line
		with open(fileName, 'rU') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			# Get the headers for the CSV file
			fieldList = {}
			for row in readCSV:
				if(row[0].startswith('f')):
					fieldList[int(row[0][1:])] = row[1]
				else:
					fieldList[int(row[0])] = row[1]

		return OrderedDict(sorted(fieldList.items()))

	def readFieldKeysFile(self, fileName):
		# Open the CSV file and process it line by line
		with open(fileName, 'rU') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			# Get the headers for the CSV file
			fieldList = {}
			for row in readCSV:
				row[0] = row[0].replace('P','')
				if(self.RepresentsInt(row[0])):
					fieldList[int(row[0])] = row[1]

		return OrderedDict(sorted(fieldList.items()))

	def getMissingPointData(self,orderedReportData, orderedPointData):
		print '-----------------------------------------------------------------'
		print 'Missing data from point PDS database:'
		missingPointData = orderedReportData.viewkeys() - orderedPointData.viewkeys()
		for key in missingPointData:
			if orderedReportData[key] != '':
				print key, orderedReportData[key]

	def comparePointAndReportData(self,orderedReportData, orderedPointData):
		now = str(time.time())
		f = open('/Users/l-z-livingston/Documents/pointDataCompare'+now+'.csv', 'w')
		f.write(self.headers+'\n')
		sharedData = orderedReportData.viewkeys() & orderedPointData.viewkeys()
		sharedData = list(sharedData)
		sharedData.sort()
		print '-----------------------------------------------------------------'
		print 'Differences between Point PDS database and report:'

		for key in sharedData:
			if(orderedReportData[key] != orderedPointData[key]):
				print '-----------------------------------------------------------------'
				print 'Not Matched key', key, ' Field Name: ', self.keyFieldValue.get(key, 'No mapping for name')
				print 'Point:= ',orderedPointData[key]
				print 'Report:= ', orderedReportData[key]
				print self.similar(orderedPointData[key], orderedReportData[key])
				f.write(str(key)+',"'+self.keyFieldValue.get(key, 'No mapping for name')+'","'
				        +str(orderedPointData[key])+'","'+str(orderedReportData[key])+ '"\n')
		f.close()

	def merge_two_dicts(self,x, y):
		"""Given two dicts, merge them into a new dict as a shallow copy."""
		z = x.copy()
		z.update(y)

		return z

	def readLogFile(self,fileName):
		with open(fileName, 'r+') as file:
			for line in file:
				if 'Unsupported field' in line:
					endOfIntro = 'feature.'
					return self.parseUnsupportedFields(line[line.find(endOfIntro) + len(endOfIntro):])

	def parseUnsupportedFields(self,unsupportedFields):
		unsupportedList = {}
		allFields = unsupportedFields.split('-')
		for field in allFields:
			splitFields = field.split(' ')
			if len(splitFields) >= 5 and splitFields[3].startswith('f'):
				unsupportedList[int(splitFields[3][1:])] = ''

		return OrderedDict(sorted(unsupportedList.items()))

newComp = ComparePointToReportData()
newComp.setPointDataFile('/Users/l-z-livingston/Downloads/1443612-fields.csv')
newComp.setDataFolder('/Users/l-z-livingston/Downloads/Reports')
newComp.compareAll()
