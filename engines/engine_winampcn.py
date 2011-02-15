#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_winampcn.py

import engine,urllib,re,sys

def htmlDecode(string):
	entities={'&apos;':'\'','&quot;':'"','&gt;':'>','&lt;':'<','&amp;':'&'}
	for i in entities:
		string=string.replace(i,entities[i])
	return string

class winampcn(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='gb18030'
	
	def parser(self,response):
		b=[]
		response=unicode(response,'gb18030').encode('utf8')
		for line in response.splitlines():
			if line.startswith("  <LyricUrl"):
				artist=re.search("Artist=\"([^\"]*)\"",line).group(1)
				title=re.search("SongName=\"([^\"]*)\"",line).group(1)
				url=re.search("<\!\[CDATA\[([^\"]*)\]\]>",line).group(1)
				if(url==None):
					continue
				if(artist==None):
					artist=' '
				if(title==None):
					title=' '
				b.append([artist,title,url])
		if len(b) == 0:
			return None
		return b
			
	
	def request(self,artist,title):
		artist=unicode(artist,self.locale).encode('gb18030')
		title=unicode(title,self.locale).encode('gb18030')
		artist=urllib.quote(artist)
		title=urllib.quote(title)
		url='http://www.winampcn.com/lyrictransfer/get.aspx?song=%s&artist=%s&lsong=%s&Datetime=20060601' % (title,artist,title)
		try:
			file=urllib.urlopen(url,None,self.proxy)
			originalLrc=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			lrcList=self.parser(originalLrc)
			return (lrcList,False)

