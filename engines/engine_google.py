#!/usr/bin/env python
#-*- coding: UTF-8 -*-
# Filename: engine_google.py

#import engine,urllib,socket,re
import engine,urllib,urllib2,re
from BeautifulSoup import BeautifulSoup

def repl(matchobj):#converts html entities like &#[0-9]+; to the expected unicode char
	return unichr(int(matchobj.group(1))).encode('utf-8')

def htmlDecode(string):
	string=re.sub("\&\#([0-9]+)\;",repl,string)
	entities={'&apos;':'\'','&quot;':'"','&gt;':'>','&lt;':'<','&amp;':'&'}
	for i in entities:
		string=string.replace(i,entities[i])
	return string

class google(engine.engine):
	
	def __init__(self,proxy,locale="utf-8"):
		engine.engine.__init__(self,proxy,locale)
		self.needCheck=True
		
	def getText(self,html):
		text=""
		for part in html.contents:
			if str(type(part)) == '<type \'instance\'>':
				text+=self.getText(part)
			else:
				text+=str(part)
		return text
		
	def startsWithTag(self,text):
		tags=["ar","ti","al","by","la","offset"]
		for tag in tags:
			if text.lower().startswith(tag):
				return True
		return False
	
	def findNextTag(self,text):
		index=len(text)
		tags=["ar","ti","al","by","la","offset"]
		for tag in tags:
			pos=text.lower().find(" "+tag)
			if pos != -1 and pos < index:
				index=pos
		return index

	def request(self,artist,title):
		query="\"%s\" \"%s\" filetype:lrc" % (artist,title)
		url="http://www.google.com/search?hl=en&q=%s&btnG=Search&meta=" % (urllib.quote_plus(query))
		req=urllib2.Request(url)
		req.add_header("User-Agent","IE6 :D")
		if self.proxy:
			opener = urllib2.build_opener(urllib2.ProxyHandler(self.proxy))
		else:
			opener = urllib2.build_opener()
		try:
			html=opener.open(req).read()
		except:
			return (None,True)
		soup=BeautifulSoup(html)
		ol=soup.findAll('ol')
		if(len(ol) > 0):
			results=[]
			for result in ol[0].findAll('li'):
				a=result.findAll('a')[0]
				text=self.getText(a)
				text=htmlDecode(text)
				title=artist=""
				if re.search("\[ar:([^\]]+)",text):
					artist=re.search("\[ar:([^\]]+)",text).group(1)	
				if re.search("\[ti:([^\]]+)",text):
					title=re.search("\[ti:([^\]]+)",text).group(1)
				if (artist == "" or title == ""):
					temp=text
					while self.startsWithTag(temp):
						tag=temp.lower()[:2]
						if tag=="ar" and artist=="":
							artist=temp[2:self.findNextTag(temp)]
						elif tag=="ti" and title=="":
							title=temp[2:self.findNextTag(temp)]
						temp=temp[self.findNextTag(temp)+1:]
				url=a['href']
				if artist != "" and title != "":
					results.append([artist,title,url])
				elif re.search("\[[0-9]+:[0-9]+",text):
					results.append([text,"",url])
			if results:
				return (results,None)
		return (None,False)

