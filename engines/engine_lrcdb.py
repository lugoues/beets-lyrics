#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_lrcdb.py

import engine,urllib,re

class lrcdb(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='utf8'
	
	def lrcdbParser(self,r,artist,title):
		result=[]
		lines=r.splitlines()
		for i in lines:
			if('exact:' in i):
				lrcId=i.split(' ')[1]
			elif('partial:' in i):
				lrcId=re.search('partial: (\d+)\t',i).group(1)
			else:
				continue
			url='http://www.lrcdb.org/lyric.php?lid=%s&astext=yes' %lrcId
			result.append([artist,title,url])
		return result
			
	
	def request(self,artist,title):
		query={'artist':str(unicode(artist,self.locale).encode('utf8')),'title':str(unicode(title,self.locale).encode('utf8')),'album':'','query':'plugin','type':'plugin','submit':'submit'}
		try:
			file=urllib.urlopen('http://www.lrcdb.org/search.php',urllib.urlencode(query),self.proxy)
			originalLrc=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			if(originalLrc=='no match'):
				return (None,False)
			else:
				lrcList=self.lrcdbParser(originalLrc,artist,title)
				return (lrcList,False)

