#!/usr/bin/env python
# -*- coding: utf-8 -*-

#mark为待做

from urllib2 import Request, URLError, urlopen, ProxyHandler
import urllib2
import cookielib
import re
import urllib
import os
import chardet
import sys
import cookielib
import logging
import json
import atexit

#单例类
class Pycrwal:
	__instance=None
	def __new__(cls,*args,**kwd):
		if Urlsingle.__instance is None:
			Urlsingle.__instance=object.__new__(cls,*args,**kwd)
		return Urlsingle.__instance

	#是否用了logging系统
	log_flag = False
	def set_log_flag(f):
		self.log_flag = f


	#header为一个字典，有时间再实现为一个类包含的key有
	#User-Agent(必须）,Referer,Cookie，其余常见的header默认实现了，如果没有则不用写
	def get_url_content(self,header,url, retry_times=3 ,timeout_p=5):
		self.header = header
		try:
			send_headers = {
				'User-Agent': header['User-Agent'],
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Connection': 'keep-alive',
				'Upgrade-Insecure-Requests': 1,
				}
			if 'Referer' in header.keys():
				send_headers['Referer'] = header['Referer']
			if 'Cookie' in header.keys():
				send_headers['Cookie'] = header['Cookie']

			req = Request(url, headers=send_headers)
			html_content = urllib2.urlopen(req,timeout=timeout_p).read() # 此处对中文字符进行了转码
			#print html_content
		except Exception, e:
			#logging.warning('connection wrong： ')
			html_content = None
			print "retry times left:", retry_times
			#logging.warning('retry times left '+str(retry_times) +'times')
			if retry_times > 0:
				#if hasattr(e, 'code') and 500 <= e.code < 600:
				html_content = self.get_url_content(header,url, retry_times - 1,timeout_p)
			else:
				if self.log_flag == True:
					logging.warning('download fail(retry times >5)')

		return html_content

	#保存图片仍然设计get_url_content,所以需要header，不传则默认用get_url_content
	#要求传入参数为'utf-8'对象（mark：待改为str流）
	#用法示例
	def save_pic_urllib(self,save_path, pic_url, pic_title, pic_type,header = None):
		if header == None:
			if hasattr(Pycrwal, 'header'):
				header = self.header
			#assert header!=none
			else:
				print 'header is None'
				sys.exit(0)

		save_pic_name = save_path + pic_title +'.'+pic_type	
		if not os.path.exists(save_pic_name):
			#print save_pic_name.decode('iso-8859-2').encode('mbcs')
			#urllib.urlretrieve(pic_url, save_pic_name)
			#这种方法对https强转http保存的方法不适用，所以用下面的方式
			html_content = self.get_url_content(header,pic_url,5,3)
			if html_content != None:
				#编码问题，文件内容可以自动智能探测编码（decode），所以写入时候不用decode
				#然而这里性质不一样，open函数有两种重载，意识接受一个字节流，它会用一个默认的编码去decode，
				#然后encode成gbk字节流供操作系统识别，或者原封不动把原编码字节流写进去，windows直接用gbk解码显示，
				#和cmd不同的是，windows文件系统如果解码不出来某个字符不会像cmd抛出异常而是用默认字符显示
				#二是传入一个unicode对象，那么就直接对这个unicode对象encode成gbk就可以了，显然这一种方法不容易乱码
				f=open(save_pic_name.decode('utf-8'),'wb')#必须是二进制形式，否则会图片乱码
				print >>f,html_content
				return 1
			else :#图片失效，进行log
				if self.log_flag == True:
					logging.warning('unable get pic '+save_pic_name)
				print 'unable get pic'
				print save_pic_name
				return 0
