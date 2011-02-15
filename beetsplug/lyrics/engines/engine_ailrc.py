# -*- coding: utf-8 -*-
# +----------------------------------------+
# |Author: Lau Gin San (CopyLiu)           |
# |Email:copyliu@gmail.com                 |
# |                                        |
# |License:GPLv2.0                         |
# +----------------------------------------+

import urllib, re, engine
from HTMLParser import HTMLParser


class TilteParser (HTMLParser):
	def __init__(self):
		self.title=""
		self.readingTitle=0
		HTMLParser.__init__(self)
	def handle_starttag(self,tag,attrs):
		if tag=="title":
			self.readingTitle=1
	def handle_data(self,data):
		if self.readingTitle:
			self.title+=data
	def handle_endtag(self,tag):
		if tag=="title":
			self.readingTitle=0
	def getTitle(self):
		return self.title
#ailrc="http://ailrc.com/"

class ailrc(engine.engine):

	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='gb18030'

	def request(self,artist,title):
		try:
			n = unicode(title,self.locale).encode('utf-8')
			s = unicode(artist,self.locale).encode('utf-8')
			a = ''
			tp=TilteParser()
			n=urllib.quote(n)
			s=urllib.quote(s)
			#a=urllib.quote(a)
			result=[]
			searchurl="http://ailrc.com/AiLrc_Search.aspx?N="+n+"&S="+s+"&A="+a
			try:
				res=urllib.urlopen(searchurl)
				html=res.read()
			except IOError:
				return (None,True)
			else:
				p=re.compile("html/\d+/[A-Z]+.htm")
				temp=p.findall(html)
				links=[]
				for k in temp:
					if k not in links:
						links.append(k)
				#print links

				for url in links:
					res=urllib.urlopen("http://ailrc.com/"+url)
					html=res.read()
					tp.feed(html)
					title=tp.getTitle()
					title=unicode(title,"utf-8")
					dlr=re.compile('"(http://www.ailrc.com/ailrc_downlrc.aspx\?id=[\w%]+)"')
					dlrp=dlr.search(html)
					downurl=dlrp.group(0).replace('"','')
					p=u"(.+)\-(.+)\-(.*)\-LRC歌词下载\-爱词酷歌词网WWW\.AiLRC\.COM"
					tr=re.compile(p)
					temp=tr.match(title)
					info=temp.groups()
					result.append([info[0].encode("utf-8"),info[1].encode("utf-8"),downurl])
				if(len(result)==0):
					return (None,False)
				else:
					return (result,False)
		except:
			return (None,False)
			
			
			
	def downIt(self,url):
		import urllib2
		#print url
		try:
			req=urllib2.Request(url)
			req.add_header('Referer','http://www.ailrc.com/')
			ff=urllib2.urlopen(req)
			#ff=urllib.urlopen(url,None,self.proxy)
			originalLrc=ff.read()
			ff.close()
		except IOError:
			return (None,True)
		else:
			if(self.needCheck):
				if(self.netEncoder == None or self.netEncoder.startswith("utf-16") or self.netEncoder.startswith("utf-32")):
					if not self.validLrc(originalLrc):
						originalLrc = None
				elif(not re.search('\[\d{1,}:\d{1,}.*?\]',originalLrc)):
					originalLrc=None
			return (originalLrc,False)
	
