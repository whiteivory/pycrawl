#!/usr/bin/env python
# -*- coding: utf-8 -*-

#所爬取的网站utf-8编码

#notice表示需要注意的地方
#custom表示每个程序对于这个地方需要手工修改一下
#import重要总结
import re
import os
import logging
import sys
import chardet
from classes.pycrawl import Pycrawl
from classes.util import Util
from urlspecify.urlsingle_pmj import  Urlsingle

pc = Pycrawl()
util = Util()
urlsingle = Urlsingle()

logging.basicConfig(filename='log\\pmj_d.log',level=logging.DEBUG)

header_dic ={}
header_dic['User-Agent'] = urlsingle._useragent_c
header_dic['Cookie'] = urlsingle._cookie_c


def get_urls(content):
	reg = '<img src="(.*?)"'
	patten = re.compile(reg, re.S)
	return patten.findall(content)

def get_pics(html_content):
	#print chardet.detect(html_content) utf-8
	reg = u'zoomfile="(.*?)" file'.encode('utf-8')#notice: custom:
	patten = re.compile(reg,re.S)
	tmp =  patten.findall(html_content)
	return tmp

file_o = open ("t.html","r")
content = file_o.read()

names = get_urls(content)
for i in range(len(names)):
	url = names[i].split('@')[-1]
	name = names[i]
	name = re.sub('./','',name)
	name = name.decode('mbcs').encode('utf-8')
	url = "http://www.mojingok.com/"+url
	save_path = "savejpdir_selected\\"+name+"\\"
	# print chardet.detect(save_path)
	util.mkdir(save_path.decode('utf-8').encode('mbcs'))
	son_html = pc.get_url_content(header_dic,url,5,5)
	if son_html:
		print "downlod "+url
		# f=open('out.txt','w')
		# print >>f,son_html
		pics = get_pics(son_html)
		# print pics
		if not pics:
			print '-----fail to get pics-----'
			logging.info('fail t get pics')
			sys.exit(0)
		else:
			save_path = save_path.decode('utf-8').encode('mbcs')
			for j in range(len(pics)):
				pic_title = name +"num"+str(j)
				if not os.path.exists(save_path+pic_title.decode('utf-8').encode('mbcs')+'.jpg'):
					pic_url = pics[j].decode('utf-8').encode('mbcs')
					if not (pic_url[0] == 'h' and pic_url[1]=='t'):
						pic_url = urlsingle._rooturl + pic_url
					print pic_url
					pic_title = pic_title.decode('utf-8').encode('mbcs')

					suc = pc.save_pic_urllib(save_path,pic_url,pic_title,'jpg')
					if suc == 0:
							print '------save fail-----'
							logging.info('fail t get pic')
							sys.exit(0)
	else:
		print "--fail to get son_html--"
		logging.info('fail to get son_html')
