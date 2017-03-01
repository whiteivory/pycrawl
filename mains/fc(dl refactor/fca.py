#!/usr/bin/env python
# -*- coding: utf-8 -*-


from classes.pycrawl import Pycrawl
from classes.util import Util
from urlspecify.urlsingle_fca import  Urlsingle
import chardet
import re
import os
import logging
import sys

import atexit
import json

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf 
import xlwt

global gstart_page
global gstart_pos
global gstart_line

#单例类初始化
sigle = Urlsingle()
util = Util()
pc = Pycrawl()

#log 初始化
logging.basicConfig(filename='log\\fca.t.log',level=logging.DEBUG)

header_dic ={}
header_dic['User-Agent'] = sigle._useragent_c
header_dic['Cookie'] = sigle._cookie_c

header_dic_ajax={}
header_dic_ajax['User-Agent'] = sigle._useragent_c
header_dic_ajax['Cookie'] = sigle._cookie_c
header_dic_ajax['Referer'] = sigle._referer


#return date,cate,title,download,source,link
def get_line_content(html_content):
    pic_reg = '<span class="movT2"><span class="addt">(.*?)&nbsp;(.*?)</span>(?:.*?)href="[0-9]+/" >(.*?)</a>(?:.*?)href="(.*?)" >(.*?)</a>(?:.*?)class="files">(.*?)</span>(?:.*?)href="(?:.*?)>(.*?)</a>'
    patten = re.compile(pic_reg, re.S)
    #f=open('out.txt','w')
    #print >>f,html_content 
    return patten.findall(html_content)

def decrateSheetLine(arr):
	date = '2017/'+arr[0].split('-')[0]+'/'+arr[0].split('-')[1]+' '+arr[1]
	cate = arr[2]
	href = sigle._rooturl+arr[3][1:]
	title = arr[4]
	download = arr[5]
	source = arr[6]
	look_num = arr[7]
	com_num = arr[8]
	down_num = arr[9]
	rate = str(float(down_num) / float(look_num)) #转换成str是为了decode
	return (date,cate,title,href,look_num,com_num,down_num,rate,download,source)


#@todo: 给arr加一个adapter让这个函数更纯粹
def writeline(sheet,arr):
	global gstart_line
	arr_d = decrateSheetLine(arr)
	colnum = len(arr_d)
	for i in range(colnum):
		sheet.write(gstart_line,i,arr_d[i].decode('utf-8'))
	gstart_line = gstart_line+1

#加refer
def get_commenturlajax_content(url, refer,retry_times=3 ,timeout_p=3):
	header_dic_ajax['Referer']=refer
	html_content = pc.get_url_content(header_dic_ajax,url,retry_times,timeout_p)
	if html_content == None:
		logging.warning('fetch comment num fail(retry times>5)')
	return html_content


def init():
    global gstart_page
    global gstart_pos
    global gstart_line
    file = open("init_a.txt")
    arr= []
    while 1:
        line = file.readline()
        if not line:
            break
        arr.append(int(line))

    gstart_page = arr[0]
    print gstart_page
    gstart_pos  = arr[1]
    print gstart_pos
    gstart_line = arr[2]
    file.close()

def save_2_file(wb):
    global gstart_page
    global gstart_pos
    global gstart_line
    file = open("init_a.txt","w")
    file.write(str(gstart_page)+'\n')
    file.write(str(gstart_pos)+'\n')
    file.write(str(gstart_line)+'\n')
    file.close()
    wb.save('A.xls')

 #这个网站编码比较奇怪，不能用mbcs来存储，只能用str来fopen，或许最正确的方式应该是fopen
def save_pic_urllib(save_path, pic_url, pic_title, pic_type):
    save_pic_name = save_path + pic_title +'.'+pic_type
    if not os.path.exists(save_pic_name):
        html_content = get_url_content_forpic(pic_url,5,3)
        if html_content != None:
            f=open(save_pic_name.decode('utf-8'),'wb')#必须是二进制形式，否则会图片乱码
            print >>f,html_content
            return 1
        else :#图片失效，进行log
            return 0

def get_comm_num(page_id,son_url):
    comment_url = sigle._commenturl%page_id
    comment_json = get_commenturlajax_content(comment_url,refer=son_url)
    if not comment_json:
        print u'    lvl2无法获取请求字符串'
        logging.warning('    werror6: lvl2 cannot get getcommnet response string')
    com_dic = json.loads(comment_json)
    if 'commenthits' in com_dic and 'downhits' in com_dic and 'lookhits' in com_dic:
    	comment_num = com_dic['commenthits']
    	look_num = com_dic['lookhits']
    	down_num = com_dic['downhits']
    else:
        print u'    lvl2无法从返回字符串中解析到commenthits'
        logging.warning('    werror7: lvl2 cannot get commenthits from the dict')
        comment_num = -1
        look_num = -1
        down_num = -1

    return (look_num,comment_num,down_num)

if __name__ == "__main__":
    global gstart_page
    global gstart_pos
    global gstart_line
    init()
    #不存在自己建立一个
    if not os.path.isfile('A.xls'):
        wb = xlwt.Workbook()
        ws = wb.add_sheet('A')
        actualpos = 0
    else:
        rb = open_workbook('A.xls',formatting_info=True)
        r_sheet = rb.sheet_by_index(0) # read only copy to introspect the file
        actualpos = r_sheet.nrows
        wb = copy(rb) # a writable copy (I can't read values out of this, only write to it)
        ws = wb.get_sheet(0) # the sheet to write to within the writable copy
    #assert
    if not actualpos == gstart_line:
    	print 'gstart_line 设置不正确，请检查init_a.txt第三行'

    #如果发生中断，手工设置下面的断点，不用担心下一页的起始位置，会默认设置为1

    atexit.register(save_2_file,wb)

    if gstart_pos != 0:
        print '----------------------warning-------------------'
        print 'startpos not zero '
    for index in range(gstart_page, gstart_page+100):  # 按照ID来爬整个网站
        gstart_page = index
        src = sigle._scrapyurl % (index)
        print 'try to fetch: ', src
        logging.info('start trying to fetch page_num: '+str(index))
        url_content = pc.get_url_content(header_dic,src)
        if re.search('GetCode',url_content)!=None:
            print u'要求验证码，请手工打开网站输入验证码后继续,或百度IP突破'
            logging.warning('werror1: yanzhengma')
            f=open('out.txt','wb')
            print >>f,url_content
            f.close() 
            exit(0)
        if url_content:
            print u'有内容开始解析'
            logging.info('lvl1 have content ,start parsing--')
            lt_list = get_line_content(url_content)
            if not lt_list:
                print 'lvl1 werror3: this page has content but not any link?'
                logging.warning('werror3: this page has content but not any link?')
                f=open('out.txt','wb')
                print >>f,url_content
                f.close() 
                exit(0)
            for i in range(gstart_pos,len(lt_list)):
                gstart_pos = i
                print '    number: '+str(i)+' link'
                link = lt_list[i][3]
                page_id = link.split('/')[4].split('.')[0]
                print "    _id: "
                print "    "+page_id
                logging.info('    try to fetch page_id: '+str(page_id))
                #title = lt_list[i][1]
                # print u'连接为： '+link
                son_url = sigle._rooturl+link

                #son_content = pc.get_url_content(header_dic,son_url,5,3)
                #if son_content:
                    #print '    lvl2 has content start parsing'
                    #logging.info('    lvl2 has content start parsing')
                num_tuple =get_comm_num(page_id,son_url)
                construct_tuple = lt_list[i] + num_tuple
                writeline(ws,construct_tuple)
            gstart_pos = 0
            print 'page'+str(index)+' complete-----'
        else:
            print 'lvl1 after 5 tries num '+str(index)+' page download fail'
            logging.warning('werror2: lvl1 after5 tries num '+str(index)+' page download fail')
    wb.save('A.xls')
