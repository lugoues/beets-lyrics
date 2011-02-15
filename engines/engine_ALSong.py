#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_ALSong.py
#
# Note: part of this code is taken from the LyricsScreenlet project
# You can see it at http://code.google.com/p/lyrics-screenlet/
# I hope they don't get it wrong, but they seems to use our MiniLyrics script
# so I allowed myself to use part of teir code (under GPL).

import engine,urllib2,re

class ALSong(engine.engine):

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
	
	def request(self,artist,title):
		if type(title) != type(u""):
			title = unicode(title,self.locale)
		if type(artist) != type(u""):
			artist = unicode(artist,self.locale)
		
		artist_enc = self.htmlEncode(artist)
		title_enc = self.htmlEncode(title)
		#print artist,title
		
		url = "http://lyrics.alsong.net/alsongwebservice/service1.asmx"
		request = """<?xml version="1.0" encoding="UTF-8"?>
		<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns1="ALSongWebServer">
			<SOAP-ENV:Body>
				<ns1:GetResembleLyric2Count>
					<ns1:stQuery>
						<ns1:strTitle>%s</ns1:strTitle>
						<ns1:strArtistName>%s</ns1:strArtistName>
					</ns1:stQuery>
				</ns1:GetResembleLyric2Count>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>""" % (title_enc,artist_enc)

		req=urllib2.Request(url,request)
		req.add_header('Content-Type','text/xml; charset=utf-8')
		if self.proxy:
			opener = urllib2.build_opener(urllib2.ProxyHandler(self.proxy))
		else:
			opener = urllib2.build_opener()
		try:
			xml = opener.open(req).read()
		except:
			return (None,True)
		count = re.search(r"<strResembleLyricCount>(\d*)</strResembleLyricCount>",xml,re.DOTALL)
		if count:
			count = int(count.group(1))
			#print count
			if count <= 0:
				return (None,False)
			request = """<?xml version="1.0" encoding="UTF-8"?>
		<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns1="ALSongWebServer">
			<SOAP-ENV:Body>
				<ns1:GetResembleLyric2>
					<ns1:stQuery>
						<ns1:strTitle>%s</ns1:strTitle>
						<ns1:strArtistName>%s</ns1:strArtistName>
						<ns1:nCurPage>0</ns1:nCurPage>
					</ns1:stQuery>
				</ns1:GetResembleLyric2>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>""" % (title_enc,artist_enc)
			req=urllib2.Request(url,request)
			req.add_header('Content-Type','text/xml; charset=utf-8')
			try:
				xml = opener.open(req).read()
			except:
				return (None,True)
			results = re.findall(r"<strTitle>\s*(.*?)\s*</strTitle>\s*<strLyric>\s*(.*?)\s*</strLyric>\s*<strArtistName>\s*(.*?)\s*</strArtistName>",xml,re.DOTALL)
			results = list(results)
			for i in range(len(results)):
				results[i] = list(results[i])
				for j in range(3):
					results[i][j] = self.htmlDecode(results[i][j])
					results[i][j] = re.compile(r"<br\s*/?>",re.DOTALL | re.IGNORECASE).sub("\n",results[i][j])
				results[i] = (results[i][2], results[i][0], results[i][1])
			results = self.orderResults(results,artist,title)
			if(len(results) > 0):
				return (results,False)
		return (None,False)

	def downIt(self,lyrics):
		if not self.validLrc(lyrics):
			lyrics = None
		elif(not re.search('\[\d{1,}:\d{1,}.*?\]',lyrics)):
			lyrics=None
		return (lyrics,False)


