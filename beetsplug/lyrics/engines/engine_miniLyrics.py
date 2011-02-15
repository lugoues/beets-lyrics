#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_miniLyrics.py

#import engine,re,socket,md5,urllib
try:
	from hashlib import md5
except:
	from md5 import md5
import engine,re,urllib,urllib2

class miniLyrics(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder=None
	
	def htmlEncode(self,string):
		chars={'\'':'&apos;','"':'&quot;','>':'&gt;','<':'&lt;','&':'&amp;'}
		for i in chars:
			string=string.replace(i,chars[i])
		return string
		
	def htmlDecode(self,string):
		entities={'&apos;':'\'','&quot;':'"','&gt;':'>','&lt;':'<','&amp;':'&'}
		for i in entities:
			string=string.replace(i,entities[i])
		return string
	
	def miniLyricsParser(self,response):
		lines=response.splitlines()
		ret=[]
		for line in lines:
			if line.strip().startswith("<fileinfo filetype=\"lyrics\" "):
				loc=[]
				loc.append(self.htmlDecode(re.search('link=\"([^\"]*)\"',line).group(1)))
				if not loc[0].lower().endswith(".lrc"):
					continue
				if(re.search('artist=\"([^\"]*)\"',line)):
					loc.insert(0,self.htmlDecode(re.search('artist=\"([^\"]*)\"',line).group(1)))
				else:
					loc.insert(0,' ')
				if(re.search('title=\"([^\"]*)\"',line)):
					loc.insert(1,self.htmlDecode(re.search('title=\"([^\"]*)\"',line).group(1)))
				else:
					loc.insert(1,' ')
				ret.append(loc)
		return ret
	
	def request(self,artist,title):
		xml ="<?xml version=\"1.0\" encoding='utf-8'?>\r\n"
		xml+="<search filetype=\"lyrics\" artist=\"%s\" title=\"%s\" " % (self.htmlEncode(unicode(artist,self.locale).encode('utf8')),self.htmlEncode(unicode(title,self.locale).encode('utf8')))
		xml+="ProtoVer=\"0.9\" client=\"lrcShow-X for Linux\" ClientCharEncoding=\"iso-8859-15\"/>\r\n"
		md5hash=md5(xml+"Mlv1clt4.0").digest()
		request="\x02\x00\x04\x00\x00\x00%s%s" % (md5hash,xml)
		del md5hash,xml
		
		url="http://www.viewlyrics.com:1212/searchlyrics.htm"
		req=urllib2.Request(url,request)
		req.add_header("User-Agent","MiniLyrics")
		if self.proxy:
			opener = urllib2.build_opener(urllib2.ProxyHandler(self.proxy))
		else:
			opener = urllib2.build_opener()
		try:
			response=opener.open(req).read()
		except:
			return (None,True)
		
		lrcList=self.miniLyricsParser(response)
		if(len(lrcList)==0):
			return (None,False)
		else:
			return (self.orderResults(lrcList,artist,title),False)

