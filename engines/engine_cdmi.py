#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_cdmi.py

import engine,urllib2,urllib,re

class cdmi(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='utf8'
	
	def request(self,artist,title):
		url = '%s - %s' % (str(unicode(artist,self.locale).encode('utf8')),(unicode(title,self.locale).encode('utf8')))
		url = urllib.quote(url)
		url = 'http://www.cdmi.net/LRC/cgi-bin/lrc_search.cgi?lrc_id=%s' % url
		try:
			#print url
			opener = urllib2.build_opener(urllib2.HTTPRedirectHandler,urllib2.ProxyHandler(self.proxy))
			file=opener.open(url)
			originalLrc=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			if(originalLrc.startswith('[ti:No Lyrics]')):
				return (None,False)
			else:
				value = re.findall(r"\[ar:(.*?)\]",originalLrc)
				if value:
					artist = value[0]
				value = re.findall(r"\[ti:(.*?)\]",originalLrc)
				if value:
					title = value[0]
				return ([[artist,title,originalLrc]],False)
	#def downIt(self,url):
		#return url

