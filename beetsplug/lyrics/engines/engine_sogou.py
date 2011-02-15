#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_sogou.py

import engine,re,urllib

class sogou(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='gb18030'
	
	def changeUrlToGb(self,info):
		address=unicode(info,self.locale).encode('gb18030')
		return address
	
	def sogouParser(self,a):
		wList=[]
		for i in a:
			b=urllib.unquote_plus(i.split('=')[-1])
			c=unicode(b,'gb18030').encode('utf8')
			title,artist=c.split('-',1)
			wList.append([artist,title,i])
		return wList
	
	def request(self,artist,title):
		url1='http://mp3.sogou.com/gecisearch.so?query='
		url2_pre='%s %s' %(self.changeUrlToGb(title),self.changeUrlToGb(artist))
		url2=urllib.quote_plus(url2_pre)
		url=url1+url2
		
		try:
			file=urllib.urlopen(url,None,self.proxy)
			lrc_gb=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			tmp=unicode(lrc_gb,'gb18030').encode('utf8')
			tmpList=re.findall('href=\"downlrc\.jsp\?tGroupid=.*?\"',tmp)
			if(len(tmpList)==0):
				return (None,False)
			else:
				tmpList=map(lambda x: re.sub('href="|"','', 'http://mp3.sogou.com/'+x), tmpList)
				lrcList=self.sogouParser(tmpList)
				#return (lrcList,False)
				#lrcUrlPre=re.sub('href="|"','',tmpList[0])
				#lrcUrl='http://mp3.sogou.com/'+lrcUrlPre
				#print lrcUrlPre
				return (lrcList,False)

