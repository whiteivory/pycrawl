#!/usr/bin/env python
# -*- coding: utf-8 -*-
from classes.pycrawl import Pycrawl
from classes.util import Util
from urlspecify.urlsingle_fc import  Urlsingle
import chardet
import re
import os
import logging
import sys

import atexit
import json

global gstart_page
global gstart_pos

#单例类初始化
sigle = Urlsingle()
util = Util()
pc = Pycrawl()

#log 初始化
logging.basicConfig(filename='log\\2.24.log',level=logging.DEBUG)

header_dic ={}
header_dic['User-Agent'] = sigle._useragent_c
header_dic['Cookie'] = sigle._cookie_c

header_dic_ajax={}
header_dic_ajax['User-Agent'] = sigle._useragent_c
header_dic_ajax['Cookie'] = sigle._cookie_c
header_dic_ajax['Referer'] = sigle._referer

header_dic_pic={}
header_dic_pic['User-Agent'] = sigle._useragent_c


def get_pic_title_and_url(html_content):
    pic_reg = 'alt="(.*?)" src="((?:http|https)://.*?(png|jpg|gif))"'
    patten = re.compile(pic_reg, re.IGNORECASE)
    #f=open('out.txt','w')
    #print >>f,html_content 
    return patten.findall(html_content)

def get_link(html_content):
    link_reg = 'class="title(?:.*?)href="(.*?)"'
    patten = re.compile(link_reg, re.IGNORECASE)
    return patten.findall(html_content)

def get_tilte(html_content):
    reg = '<title>(.*?)</title>'
    title = re.search(reg,html_content).group(1)
    return title

def get_pics(html_content):
    reg = '\[img\]((.*?)(jpg|png|gif))(?:.*?)\['
    patten = re.compile(reg,re.IGNORECASE)
    return patten.findall(html_content)

#加refer
def get_commenturlajax_content(url, refer,retry_times=3 ,timeout_p=3):
	header_dic_ajax['Referer']=refer
	html_content = pc.get_url_content(header_dic_ajax,url,retry_times,timeout_p)
	if html_content == None:
		logging.warning('fetch comment num fail(retry times>5)')
	return html_content

#图片不需要cookie
def get_url_content_forpic(url, retry_times=3 ,timeout_p=5):
	html_content = pc.get_url_content(header_dic_pic,url,retry_times,timeout_p)
	if html_content == None:
		 logging.warning('download pic fail(retry times >5)')
	return html_content

def init():
    global gstart_page
    global gstart_pos
    file = open("init.txt")
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
    file.close()

def save_2_file():
    global gstart_page
    global gstart_pos
    file = open("init.txt","w")
    file.write(str(gstart_page)+'\n')
    file.write(str(gstart_pos)+'\n')
    file.close()

#这个网站编码比较奇怪，不能用mbcs来存储，只能用str来fopen，或许最正确的方式应该是fopen
def save_pic_urllib(save_path, pic_url, pic_title, pic_type):
    #save_pic_name = save_path + pic_url.split('/')[len(pic_url.split('/')) - 1]
    save_pic_name = save_path + pic_title +'.'+pic_type
    if not os.path.exists(save_pic_name):
        #print save_pic_name.decode('iso-8859-2').encode('mbcs')
        #urllib.urlretrieve(pic_url, save_pic_name)
        #这种方法对https强转http保存的方法不适用，所以用下面的方式
        # send_headers = {
        #     'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        # }
        # req = Request(pic_url, headers=send_headers)
        # try:
        #     html_content = urlopen(req).read()
        # except Exception, e:
        #     print u'Exception save faile'
        # else:
        #     f=open(save_pic_name,'wb')#必须是二进制形式，否则会图片乱码
        #     print >>f,html_content
        html_content = get_url_content_forpic(pic_url,5,3)
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
            return 0

if __name__ == "__main__":
    global gstart_page
    global gstart_pos

    #如果发生中断，手工设置下面的断点，不用担心下一页的起始位置，会默认设置为1
    init()
    atexit.register(save_2_file)
    continue_pos = gstart_pos
    if continue_pos != 0:
        print '----------------------warning-------------------'
        print 'startpos not zero '
    save_path = util.mkdir("savedir\\")
    for index in range(gstart_page, gstart_page+4):  # 按照ID来爬整个网站
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

            #type1 = chardet.detect(url_content)['encoding']
            #print type1+"hhhhhhhhhhh"
            # type0 = sys.getfilesystemencoding()
            # f=open('out.txt','wb')
            # print >>f,url_content
            # f.close() 
            
            #print str(index) + u"有内容"
            son_save_path = util.mkdir(save_path + str(index) + "\\")
            lt_list = get_link(url_content)#获取所有子连接
            if not lt_list:
                print 'werror3: this page has content but not any link?'
                logging.warning('werror3: this page has content but not any link?')
                f=open('out.txt','wb')
                print >>f,url_content
                f.close() 
                exit(0)
            for i in range(continue_pos,len(lt_list)):
                gstart_pos = i
            #for i in range(len(lt_list)):
                print '    number: '+str(i)+' link'
                link = lt_list[i]
                page_id = link.split('/')[4].split('.')[0]

                print "    _id: "
                print "    "+page_id
                logging.info('    try to fetch page_id: '+str(page_id))
                #title = lt_list[i][1]
                # print u'连接为： '+link
                son_url = sigle._rooturl+link

                son_content = pc.get_url_content(header_dic,son_url,5,3)
                # f=open('out.txt','wb')
                # print >>f,son_content
                # f.close() 
                if son_content:
                    # print u'子地址有内容，开始爬取：---'
                    print '    lvl2 has content start parsing'
                    logging.info('    lvl2 has content start parsing')
                    title =get_tilte(son_content)
                    #print chardet.detect(title) #这个帮助我发现了utf-8编码
                    #title_for_output = title
                    print '    '+title.decode('utf-8').encode('mbcs')
                    pics = get_pics(son_content)
                    if not title or not pics:
                        print '    werror5: lvl2 fail to parse title and pic url from the html'
                        logging.info('    werror5: lvl2 fail to parse title and pic url from the html,form may change')
                    else:
                    #测试得到评论数据
                        comment_url = sigle._commenturl%page_id
                        comment_json = get_commenturlajax_content(comment_url,refer=son_url)
                        if not comment_json:
                            print u'    lvl2无法获取请求字符串'
                            logging.warning('    werror6: lvl2 cannot get getcommnet response string')
                        com_dic = json.loads(comment_json)
                        if 'allnum' in com_dic:
                            comment_num = com_dic['allnum']
                        elif'AllNum' in com_dic:
                            comment_num = com_dic['AllNum']
                        else:
                            print u'    lvl2无法从返回字符串中解析到allnum'
                            logging.warning('    werror7: lvl2 cannot get allnum from the dict')
                            comment_num = com_dic['allnum']
                        for j in range(len(pics)):
                            pic_url = pics[j][0]
                            pic_type = pics[j][2]
                            #sub函数有正则规则，【】表示其中任意一个
                            title = re.sub('[\/:*?"<>-]','@',title) #防止题目中的-影响解析,还有其他不能作为文件名的符号

                            #编码问题：字符串的相加不要进行编码解码，这是一系列字节的相加，比如这个title不要decode('utf-8')，否则这个
                            #pic_filename会变成一个unicode对象，然而注意title本身并没有变成unicode对象，所以这个pic_filename如果以后不小心调用decode，会发生错误
                            #一般也不赞成隐式转换的发生
                            pic_filename = str(comment_num) + title + str(j) + re.sub('/','-',link)
                            #print type(pic_filename) #编码问题：输出为unicode对象（如果decode）
                            #print chardet.detect(pic_filename)
                            #将地址中的/2016/6/354234.html中的/和.去掉换成-
                            #编码问题：只要涉及字符串相加，就需要两者同种字符编码，已下面的进行举例
                            #前者如果引号前加了u,表明为unicode编码，不加则表示传统的ascii编码
                            #ascii编码是与很多编码向后兼容的，所以可以自动合并，而我们知道unicode不能表示例如韩文中文，所以不要加u，让其向后兼容
                            #或者分两行print
                            print "        lvl3: try get and save pic from the parsed url "+pic_filename.decode('utf-8').encode('mbcs')

                            whether_suc = save_pic_urllib(son_save_path,pic_url,pic_filename,pic_type)
                            if whether_suc == 0 and int(comment_num) > 2 and j==0:
                                logging.warning('        werror8: lvl3 pic load fail , comment_num: (>2)'+comment_num+' id: '+page_id)
                                logging.warning('        title:'+title.decode('utf-8'))
                                print(u'        lvl3 图片获取失败')
                            elif whether_suc == 1:
                                logging.info('        download pic success')

                            #测试用
                            # sys.exit(0)
                else:
                    print '    werror4: lvl2 after 5 tries,page donwload fail '
            continue_pos = 0 #若本页有断点，下一页正常从0开始

                # print u'标题为: '+title.decode('iso-8895-2').encode('mbcs')
            print 'page'+str(index)+' complete-----'
        else:
            print 'lvl1 after 5 tries num '+str(index)+' page download fail'
            logging.warning('werror2: lvl1 after5 tries num '+str(index)+' page download fail')