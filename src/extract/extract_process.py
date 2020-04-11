import json

class ExtractProcess:

	SOURCE_DIRECTORY = '../bible'
	
	def __init__(self):
		self._bibleVersions = dict()
		self._bibleBooks = dict()
