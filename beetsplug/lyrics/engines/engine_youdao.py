#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_youdao.py

import engine, re, urllib

class youdao(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='utf8'
	
	def changeUrlToUtf8(self,info):
		address=unicode(info,self.locale).encode('utf8')
		return address
	
	def youdaoParser(self,a):
		b=[]
		for i in a:
			r = re.search('<!--title start-->(.*?)<!--title end-->.*?<!--artist start-->(.*?)<!--artist end-->.*?<!--lyric-download-link start-->(.*?)target', i)
			try:
				_title = re.sub('</font>|</a>', '', r.group(1))
				_title = re.sub('<.*>', '', _title)
				_artist = re.sub('</font>|</a>', '', r.group(2))
				_artist = re.sub('<.*>', '', _artist)
				_url = 'http://mp3.youdao.com'+re.sub('<a href=\"|\"| ', '', r.group(3))
			except:
				pass
			else:
				b.append([_artist,_title,_url])
		return b
	
	def request(self,artist,title):
		url1='http://mp3.youdao.com/search?q='
		url3='&start=0&ue=utf8&keyfrom=music.nextPage&t=LRC&len=5'
		url2='%s+%s' %(self.changeUrlToUtf8(title),self.changeUrlToUtf8(artist))
		url=url1+url2+url3
		
		try:
			file=urllib.urlopen(url,None,self.proxy)
			lrc_utf8=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			tmpList = re.findall('<div class="info p90">.*?</a></div>', lrc_utf8)
			if(len(tmpList)==0):
				return (None,False)
			else:
				lrcList=self.youdaoParser(tmpList)
				return (lrcList,False) 
