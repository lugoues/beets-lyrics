#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_ttPlayer.py

from ttpClient import ttpClient
import engine,re,random,urllib

class ttPlayer(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='utf8'
	
	def ttplayerParser(self,a):
		b=[]
		for i in a:
			c=re.search('id=\"(.*?)\" artist=\"(.*?)\" title=\"(.*?)\"',i)
			try:
				_artist=c.group(2)
				_title=c.group(3)
				_id=c.group(1)
				entities={'&apos;':'\'','&quot;':'"','&gt;':'>','&lt;':'<','&amp;':'&'}
				for ii in entities:
					_artist = _artist.replace(ii,entities[ii])
					_title = _title.replace(ii,entities[ii])
					_id = _id.replace(ii,entities[ii])
			except:
				pass
			else:
				url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(int(_id),ttpClient.CodeFunc(int(_id),(_artist+_title)), random.randint(0,0xFFFFFFFFFFFF))
				b.append([_artist,_title,url])
		return b
	
	def request(self,artist,title):
		url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(ttpClient.EncodeArtTit(unicode(artist,self.locale).replace(u' ','').lower()), ttpClient.EncodeArtTit(unicode(title,self.locale).replace(u' ','').lower()))
		#print url
		try:
			file=urllib.urlopen(url,None,self.proxy)
			webInfo=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			tmpList=re.findall(r'<lrc.*?</lrc>',webInfo)
			if(len(tmpList)==0):
				return (None,False)
			else:
				lrcList=self.ttplayerParser(tmpList)# here lrcList must be the format like [[artist,title,url].....]
				return (lrcList,False)

