#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_evillyrics.py
#
# Some of this code is taken from the Googlyrics2 amarokscript.
# So, if you like this script, we suggest you to give a try to
# the original script at http://quicode.com/googlyircs2 (GPLv3)
#
# The conversion from Kas file to lrc is based upon the python's difflib
# 

import engine,plain_lyrics,urllib,re
from htmlentitydefs import name2codepoint as n2cp
import sys,difflib

def ms2timestamp(ms):
	mins="0%s" % int(ms/1000/60)
	sec="0%s" % int((ms/1000)%60)
	msec="0%s" % int((ms%1000)/10)
	return "[%s:%s.%s]" % (mins[-2:],sec[-2:],msec[-2:])

def purgeText(txt):
	temp=txt.splitlines()
	txt=[]
	for i in range(len(temp)):
		letters = re.findall("[^\s']{1,1}",temp[i])
		if len(letters) > 2:
			txt.append(temp[i].strip())
	return txt

def mergeTextAndKas(testo,KAS):
	if type(testo) != type([]):
		testo=purgeText(testo)
	core=re.compile("^karaoke:").sub("",KAS.split(';')[0])
	tokens=[core[i:i+2].decode("windows-1252") for i in range(len(core)) if i%4==2]
	kas=[i.lower() for i in tokens]
	times=[core[i:i+2] for i in range(len(core)) if i%4==0]
	times=[(((ord(token[0])-64)*64 + (ord(token[1])-64))*200) for token in times]

	tot=[]
	for i in range(len(kas)):
		tot.append([kas[i],times[i]])

	purge=lambda x: re.compile(r"[\s']+").sub("",x)
	txt=[purge(line)[:2].lower() for line in testo]

	d=tuple(difflib.ndiff(txt,kas))
	i=0
	j=0
	surplus=[]
	deficit=[]
	for line in d:
		if line.startswith('+'):
			surplus.append(i)
			i+=1
			continue
		elif line.startswith('-'):
			deficit.append(j)
			j+=1
			continue
		i+=1
		j+=1
	
	count=0
	for i in surplus:
		del tot[i-count]
		count+=1

	count=0
	for i in deficit:
		if(i-count > 0):
			testo[i-count-1]+=" "+testo[i-count]
		del testo[i-count]
		count+=1
	#print testo
	lrc = "\r\n".join([ms2timestamp(tot[i][1])+testo[i] for i in range(len(tot))]).encode('utf-8')
	return (lrc,(len(surplus)+len(deficit))/2.0)

class evillyrics(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		#self.netEncoder=None
		
	def request(self,artist,title):
		enc_artist = unicode(artist,self.locale).encode('windows-1252')
		enc_title = unicode(title,self.locale).encode('windows-1252')
		#url="http://www.evillabs.sk/evillyrics/getkaraoke.php?artist=%s&song=%s" % (urllib.quote_plus(artist),urllib.quote_plus(title))
		url="http://www.evillabs.sk/evillyrics/gc2.php?artist=%s&song=%s" % (urllib.quote_plus(enc_artist),urllib.quote_plus(enc_title))
		#sys.stdout.write(url+'\n')
		try:
			file=urllib.urlopen(url,None,self.proxy)
			kas=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			if(kas == "error" or kas == None):
				return (None,False)
			try:
				if (not kas.split(';')[1].isdigit()):
					return (None,False)
			except:
				return (None,False)
			else:
				#print kas
				return ([[artist,title,[artist,title,kas]]],False)
	
	def downIt(self,url):
		artist=url[0]
		title=url[1]
		kas=url[2]
		lrc = False
		if kas.split(";")[-1].lower().startswith("http://"):
			url = kas.split(";")[-1]
			lyrics,timeout = plain_lyrics.getLyricsFromUrl(url,proxy=self.proxy)
			if not timeout and lyrics:
				lrc,difference = mergeTextAndKas(lyrics,kas)
				
				if difference <= len(lyrics.splitlines())/3.0:
					try:
						lrc = "[ar:%s]\r\n[ti:%s]\r\n" % (artist,title) + lrc
					except Exception,e:
						sys.stdout.write(e+'\n')
					return (lrc,False)
		urls,timeout = plain_lyrics.getUrlsFromGoogle(artist,title,self.proxy)
		if timeout or not urls:
			if lrc:
				return (lrc,False)
			else:
				return (None,timeout)
		for url in urls:
			#sys.stdout.write(url+'\n')
			lyrics,timeout = plain_lyrics.getLyricsFromUrl(url,proxy=self.proxy)
			if not timeout and lyrics:
				lrc,difference = mergeTextAndKas(lyrics,kas)
				if difference <= len(lyrics.splitlines())/3.0:
					try:
						lrc = "[ar:%s]\r\n[ti:%s]\r\n" % (artist,title) + lrc
					except Exception,e:
						sys.stdout.write(e+'\n')
					return (lrc,False)
		if lrc:
			try:
				lrc = "[ar:%s]\r\n[ti:%s]\r\n" % (artist,title) + lrc
			except Exception,e:
				sys.stdout.write(e+'\n')
			return (lrc,False)
		return (None,False)

