#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

class Urlsingle(object):
	__instance=None
	_htmlencode = 'utf-8'
	#由于_dic中都是unicode的对象，而我源文件中都是从html中直接爬取的str字节流对象
	#所以这里是网站的编码格式，dic中的对象要全部encode成utf-8字节流
	#虽然这样总体上多此一举但是懒得改原来的代码了

	def __init__(self):
		with open('urlspecify/urls_stre.json') as json_file:
			self._dic = json.load(json_file)
		self._rooturl = self._dic['rooturl'].encode(self._htmlencode)
		self._scrapyurl = self._dic['scrapyurl'].encode(self._htmlencode)
		self._commenturl = self._dic['commenturl'].encode(self._htmlencode)
		self._useragent_f = self._dic['useragent_f'].encode(self._htmlencode)
		self._cookie_f = self._dic['cookie_f'].encode(self._htmlencode)
		self._referer = self._dic['referer'].encode(self._htmlencode)
		self._useragent_c = self._dic['useragent_c'].encode(self._htmlencode)
		self._cookie_c = self._dic['cookie_c'].encode(self._htmlencode)

	def __new__(cls,*args,**kwd):
		if Urlsingle.__instance is None:
			Urlsingle.__instance=object.__new__(cls,*args,**kwd)
		return Urlsingle.__instance

