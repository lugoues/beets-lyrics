#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_lyrdb.py

import engine,urllib,re

class lyrdb(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='utf8'
	
	def lyrdbParser(self,a):
		b=[]
		for i in a:
			c=i.split("\\")# id\title\artist
			c[0]="http://webservices.lyrdb.com/showkar.php?q=%s&useid=1" % (c[0])
			i=c[0]
			c[0]=c[2]
			c[2]=i
			b.append(c)
		return b
			
	
	def request(self,artist,title):
		artist=str(unicode(artist,self.locale).encode('utf8'))
		title=str(unicode(title,self.locale).encode('utf8'))
		url='http://webservices.lyrdb.com/karlookup.php?q=%s+%s' % (urllib.quote_plus(artist),urllib.quote_plus(title))
		try:
			file=urllib.urlopen(url,None,self.proxy)
			originalLrc=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			tmplist=originalLrc.splitlines()
			if len(tmplist) > 1:
				lrcList=self.lyrdbParser(tmplist[:-1])
				return (lrcList,False)
			else:
				return (None,False)

