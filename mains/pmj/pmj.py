#!/usr/bin/env python
# -*- coding: utf-8 -*-

#所爬取的网站utf-8编码

#notice表示需要注意的地方
#custom表示每个程序对于这个地方需要手工修改一下
#import重要总结

from classes.pycrawl import Pycrawl
from classes.util import Util
from urlspecify.urlsingle_pmj import  Urlsingle
import chardet
import re
import os
import logging
import sys

#custom：按照查看次数排序，如果正常模式则将mod=0
#改成0的同时要改pmj.json换url
mod =1 

#单例类初始化
urlsingle = Urlsingle()
util = Util()
pc = Pycrawl()

#log 初始化
logging.basicConfig(filename='log\\pmj.log',level=logging.DEBUG)

header_dic ={}
header_dic['User-Agent'] = urlsingle._useragent_c
header_dic['Cookie'] = urlsingle._cookie_c

#notice 要用re.S 表示.可以代表任何字符，包括网页上的换行符，另外()要进行转移，还有onclick前
#并不是如同f12上复制下来的空格，要从print>>f里面复制过来,其余都是不准的
#返回网站的编码 custom:utf-8
def get_pic_title_and_url(html_content):
    single = Urlsingle()
    #pic_reg = '<div class="c cl">(?:.*?)<a href="'+single._rooturl+'(.*?)"  onclick="atarget\(this\)" title="(.*?)" class="z">(?:.*?)<img src="http://(.*?)" alt'
    pic_reg = u'<div class="c cl">(?:.*?)<a href="http://www.mojingok.com/(.*?)"(?:.*?)title="(.*?)"(?:.*?)<img src="(.*?)"(?:.*?)回复">(.*?)</a>'.encode('utf-8')
    #print pic_reg
    patten = re.compile(pic_reg, re.S)
    #f=open('out.txt','w')
    #print >>f,html_content 
    return patten.findall(html_content)


#important re要求两个字符串格式相同，所以这里出现中文，改成和网站一样的编码即utf-8
#返回utf-8
#应该立一个标准，所有函数要求的传入和返回都是utf-8字符流或者都是unicode字符流
def get_pics(html_content):
	#print chardet.detect(html_content) utf-8
	reg = u'zoomfile="(.*?)" file'.encode('utf-8')#notice: custom:
	patten = re.compile(reg,re.S)
	tmp =  patten.findall(html_content)
	return tmp

#tid是sonhtml的id
def get_tid(str):
	reg = '(?:.*?)tid=(.*?)&'
	patten = re.compile(reg,re.S)
	tmp =  patten.findall(str)
	return tmp[0]

for index in range(1,35):
	print 'download page' + str(index)
	logging.info('download page'+str(index))
	url = urlsingle._scrapyurl%index
	html_content = pc.get_url_content(header_dic,url)
	if html_content:
		#f=open('out.txt','w')
		#print >>f,html_content
		ret = get_pic_title_and_url(html_content)
		save_path = "savejpdir\\"+str(index)+"\\"
		util.mkdir(save_path)
		for i in range(len(ret)):
			son_url = ret[i][0]
			title = ret[i][1]
			title = re.sub('[\/:*?"<>-]',' ',title)#题目格式化，不要替换成&，这个字符encode成gb2312不能编码，mbcs可以
			pic_url = ret[i][2]
			replynum = ret[i][3]

			#custom:在按照查看次数分类中需要转化成一般的url的格式
			#如果不按，则修改全局变量mod=0
			if mod == 1:
				tid = get_tid(son_url)
				son_url ="thread-"+str(tid)+"-1-1.html"

			if pic_url[0] != 'h' and pic_url[1]!='t':
				pic_url = urlsingle._rooturl + pic_url 
			#pic_url = "http://" + pic_url
			#print pic_url

			url4code = urlsingle._rooturl +son_url+"/"
			pic_title = replynum+"@"+title +"@"+re.sub('/','-',son_url)
			#print chardet.detect(pic_title)
			if not os.path.exists(save_path+pic_title+'.jpg'):
				save_path = save_path.decode('utf-8').encode('mbcs')
				pic_url = pic_url.decode('utf-8').encode('mbcs')
				pic_title = pic_title.decode('utf-8').encode('mbcs')
				print pic_title
				suc = pc.save_pic_urllib(save_path,pic_url,pic_title,'jpg')
				if suc == 0:
					print '------save fail-----'
					sys.exit(0)
			#print url4code
			#print url4code
			# son_html = pc.get_url_content(header_dic,url4code,5,5)
			# if son_html:
				# f=open('out.txt','w')
				# print >>f,son_html
				# pics = get_pics(son_html)
				# if not pics
				# if code == None or len(code)>20:
				# 	print title
				# 	logging.info('get code wrong:')
				# 	logging.info(title)
				# 	logging.info(code)
				# 	print code
				# 	code = 'no'
				# print code
				# pic_title = replynum+"@"+code + "@"+title + re.sub('/','-',son_url)
				# if not os.path.exists(save_path+pic_title+'.jpg'):
				# 	suc = pc.save_pic_urllib(save_path.decode('utf-8').encode('GB2312'),pic_url.decode('utf-8').encode('GB2312'),pic_title.decode('utf-8').encode('GB2312'),'jpg')
				# 	if suc == 0:
				# 		print '------save fail-----'
				# 		sys.exit(0)
	else:
		print '-------------error-------------'
		sys.exit(0)