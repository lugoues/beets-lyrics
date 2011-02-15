#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine.py

import urllib,re,os,sys

def multiSearch(engines,artist,title,proxy=None,locale="utf-8"):
	for eng_name in engines:
		try:
			if type(eng_name) == str:
				eng = getattr(__import__("engine_%s"%eng_name),eng_name)(proxy,locale)
			elif isinstance(eng_name,engine):
				if issubclass(eng_name.__class__,engine):
					eng = eng_name
				else:
					raise ValueError("'%s' is not a valid engine" % eng_name)
			elif issubclass(eng_name,engine):
				eng = eng_name(proxy,locale)
			else:
				eng = getattr(__import__("engine_%s"%eng_name),str(eng_name))(proxy,locale)
			retList,timeout = eng.request(artist,title)
			if retList != None:
				retList = tuple( (i for i in retList if cmpResult(i,(artist,title)) >= 0.7) )
			if not timeout and retList != None and len(retList) > 0:
				return (eng,retList)
		except Exception,e:
			print e
			#sys.stdout.write(e+'\n')
			continue
	return None

def orderResults(results,artist,title):
	comp = [artist,title]
	results = map(lambda x: x[1],reversed(sorted( ((cmpResult(comp,i),i) for i in results ) )))
	return results
	
def cmpResult(result,comp):
	value=similarity(result[0],comp[0])#artist
	value+=similarity(result[1],comp[1])#title
	value=value/2
	return value

def similarity(string1,string2):
	if string1.lower() == string2.lower():
		return 1
	string1=tokenize(string1.lower())
	string2=tokenize(string2.lower())
	count = len(tuple( (i for i in string1 if i in string2) ))
	return float(count)/max((len(string2), 1))

def tokenize(string):
	string=tuple( (i.lower() for i in re.findall("\w+",string) if i.lower() not in ('a','an','the')) )
	return string

def validLrc(lrc):
	partial="".join( (i for i in lrc if (ord(i) < 128 and ord(i) != 0) ) )
	return bool(re.search('\[\d{1,}:\d{1,}.*?\]',partial))

class engine:
	
	def __init__(self,proxy=None,locale="utf-8",check=True):
		if locale == None:
			locale = "utf-8"
		self.locale=locale
		self.proxy=proxy
		self.netEncoder=None
		self.needCheck=check
	
	def request(self,artist,title):
		raise NotImplementedError('request must be implemented in subclass')
		
	def downIt(self,url):
		#print url
		try:
			ff = urllib.urlopen(url,None,self.proxy)
			originalLrc = re.sub('<br/>', '\n', ff.read())
			ff.close()
		except IOError:
			return (None,True)
		else:
			if(self.needCheck):
				if(self.netEncoder == None or self.netEncoder.startswith("utf-16") or self.netEncoder.startswith("utf-32")):
					if not self.validLrc(originalLrc):
						originalLrc = None
				elif(not re.search('\[\d{1,}:\d{1,}.*?\]',originalLrc)):
					originalLrc=None
			return (originalLrc,False)
	
	def orderResults(self,results,artist,title):
		return orderResults(results,artist,title)
	
	def validLrc(self,lrc):
		return validLrc(lrc)

