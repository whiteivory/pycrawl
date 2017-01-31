#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.pycrawl import Pycrawl
from classes.util import Util
from urlspecify.urlsingle_stre import  Urlsingle
import chardet
import re
import os

#notice 要用re.S 表示.可以代表任何字符，包括网页上的换行符，另外()要进行转移，还有onclick前
#并不是如同f12上复制下来的空格，要从print>>f里面复制过来
def get_pic_title_and_url(html_content):
    pic_reg = '<div class="c cl">(?:.*?)<a href="http://www.gojiepai.com/(.*?)"  onclick="atarget\(this\)" title="(.*?)" class="z">(?:.*?)<img src="http://(.*?)" alt'
    patten = re.compile(pic_reg, re.S)
    #f=open('out.txt','w')
    #print >>f,html_content 
    return patten.findall(html_content)



#单例类初始化
urlsingle = Urlsingle()
util = Util()
pc = Pycrawl()

header_dic ={}
header_dic['User-Agent'] = urlsingle._useragent_f

for index in range(1,29):
	url = urlsingle._scrapyurl%index
	html_content = pc.get_url_content(header_dic,url)
	# print chardet.detect(html_content) #GB2312
	if html_content:
		f=open('out.txt','w')
		# print >>f,html_content 
		ret = get_pic_title_and_url(html_content)
		# print len(ret)
		save_path = "savejpdir\\"+str(index)+"\\"
		util.mkdir(save_path)
		for i in range(len(ret)):
			son_url = ret[i][0]
			title = ret[i][1]
			title = re.sub('[\/:*?"<>-]','@',title)#题目格式化
			pic_url = ret[i][2]
			pic_url = "http://" + pic_url
			print pic_url
			pic_title = title + re.sub('/','-',son_url)
			if not os.path.exists(save_path+pic_title+'.jpg'):
				pc.save_pic_urllib(save_path,pic_url,pic_title,'jpg')
