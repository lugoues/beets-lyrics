#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_baidu.py

import engine,urllib,re

class baidu(engine.engine):
	
	def __init__(self,proxy,locale=None):
		engine.engine.__init__(self,proxy,locale)
		self.netEncoder='gb18030'
	
	def changeUrlToGb(self,info):
		address=unicode(info,self.locale).encode('gb18030')
		return address
	
	def baiduParser(self,a):
		b=[]
		for i in a:
			r=re.search('href=\"(.*?)\".*?<font size="3">(.*?) - (.*?)</font></a><br>',i)
			try:
				_url=r.group(1)
				_artist=re.sub('<font.*?>|</font>','',r.group(3))
				_title=re.sub('<font.*?>|</font>','',r.group(2))
			except:
				pass
			else:
				b.append([_artist,_title,_url])
		return b
	
	def request(self,artist,title):
		url1='http://www.baidu.com/s?ie=gb2312&bs='
		url2='+filetype%3Alrc&sr=&z=&cl=3&f=8&wd='
		url3='+filetype%3Alrc&ct=0'
		url4_pre='%s %s' %(self.changeUrlToGb(title),self.changeUrlToGb(artist))
		url4=urllib.quote_plus(url4_pre)
		url=url1+url4+url2+url4+url3
		
		try:
			file=urllib.urlopen(url,None,self.proxy)
			lrc_gb=file.read()
			file.close()
		except IOError:
			return (None,True)
		else:
			tmp=unicode(lrc_gb,'gb18030').encode('utf8')
			tmpList=re.findall(r'【LRC】.*?<font size=-1>',tmp)
			if(len(tmpList)==0):
				return (None,False)
			else:
				lrcList=self.baiduParser(tmpList)
				return (lrcList,False)

