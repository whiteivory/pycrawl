#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from urlsingle import Urlsingle

#update2:图片的服务器和网站服务器不一样，f12发现不需要cookie，挤啊还是那个cookie反而会获取不到图片
#应该是404一类的错误，然而正常访问网站是不会发现这个错误的，所以专门写了一个供图片用的get函数

#update:下午突然就不能爬了，提示要验证码，即使在firefox中输入验证码仍然不可以
#我开始研究cookie，发现其实cookie中的数值无论怎样都是不变的
#然后我打开chrome，在头信息中也可以看cookie，发现chrome的cookie的uid和firefox不一样
#我就手动输入chrome的cookie（'Cookie': ..)并修改成chrome的useragent，取消安装opener
#运行发现可以运行了
#或许下次再不行了就用天行vpn登录一下网站看看uid是否可变，或者去网吧登录一下拿个uid来爬取，或者直接在网吧爬
#总之是cookie的原因没跑
#firefox的uid应该被禁了，但为什么通过浏览器就不需要验证码，这是我唯一的疑点
#还有一个有趣的现象，我的评论仍然是通过老的cookie来获取，然而可以获取到，看来针对哪个ajax并没有限制。

#待做：爬取整个网站中评论数多的文章；获取种子地址

#由于这个网站含有大量韩文，所以编码方面有些问题，保存文件名也有问题，不用太在意
#iso-8859-2

#本网站含有防大量访问机制，一段时间内大量访问会给验证码。
#试过了各种代理方式，无果，改用cookie方式，原理是网站根据cookie来判断用户
#用firefox访问，保存cookie，如果爬取过程中出现验证码问题，就登录火狐来输入验证码，再保存cookie
#程序再读取cookie，然后就可以继续了。
#保存cookie的方式用到了火狐export_cookie插件，在火狐菜单栏中-工具-exportcookie

#重启之后应该要重新弄一下cookie，重新导出一遍

#这个网站爬取到的结果和网页f12显示的结果不一样，如果正则匹配不到可以先print>>f,html_content
#查看具体到爬到的内容是什么。

#出现问题：很多时候即使是一个网站由于其历史原因还有人工原因网站的格式是不一样的
#比如本网站在16年3月的时候图片存放的地点和之前是不同的，相应的一开始获取到的out.txt里面的
#图片的格式不同，首先[IMG]改用大写，其次jpg后面加上了图片的分辨率，导致reg出错，所以要加上有必要的log并时常观察log文件
global gstart_page
global gstart_pos

def get_url_content(url, retry_times=3 ,timeout_p=5):
    try:
        #设置使用代理
        # proxy = {'http':'115.85.237.69:80'}
        # proxy_support = ProxyHandler(proxy)
        # # opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler(debuglevel=1))
        # opener = urllib2.build_opener(proxy_support)
        # urllib2.install_opener(opener)

        # proxy_handler = urllib2.ProxyHandler({'http': 'http://121.232.147.121:9000/'})
        # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
        # # proxy_auth_handler.add_password('realm', 'host', 'username', 'password')

        # opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
        # # This time, rather than install the OpenerDirector, we use it directly:
        # urllib2.install_opener(opener)
        sigle = Urlsingle()

        #cj = cookielib.MozillaCookieJar()
        #cj.load("cookies.txt")
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #urllib2.install_opener(opener)
        cookie_firefox = sigle._cookie_f
        agent_firefox = sigle._useragent_f
        refer = sigle._referer
        send_headers = {
            'User-Agent': agent_firefox,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer':refer,
            'Upgrade-Insecure-Requests': 1,
            'Cookie': cookie_firefox
            }

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
            html_content = get_url_content(url, retry_times - 1)
        else:
            logging.warning('download fail(retry times >5)')

    return html_content

#这个是通过在chromef12里network选项找到了xhr类型的一个请求，点击可以查看具体的
#request和response头和内容，一开始用的上面那个函数，结果怎么都不行
#由于本请求为ajax，于是加上了ajax的请求头还是不行
#最后从f12里面header一一复制过来测试发现是由于refer，有些网址为了防止倒链很注重refer
def get_commenturlajax_content(url, refer,retry_times=3 ,timeout_p=3):
    try:
        #cj = cookielib.MozillaCookieJar()
        #cj.load("cookies.txt")
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #urllib2.install_opener(opener)
        sigle = Urlsingle()
        cookie_firefox = sigle._cookie_f
        #print 'ccccccccccccc'+cookie_firefox
        agent_firefox = sigle._useragent_f
        #print agent_firefox
        print refer

        send_headers = {
            'User-Agent': agent_firefox,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': 1,
            'Cookie': cookie_firefox
            }
        #加上refer
        req = Request(url, headers=send_headers)
        req.add_header('Referer',refer)
        html_content = urllib2.urlopen(req,timeout = timeout_p).read() # 此处对中文字符进行了转码
        #print html_content
    except Exception, e:
        logging.warning('connection wrong： ')
        html_content = None
        print "retry times left:", retry_times
        logging.warning('retry times left '+str(retry_times) +'times')
        if retry_times > 0:
            #if hasattr(e, 'code') and 500 <= e.code < 600:
            html_content = get_commenturlajax_content(url,refer, retry_times - 1)
        else:
            logging.warning('fetch comment num fail(retry times>5)')
    return html_content

#图片不需要cookie
def get_url_content_forpic(url, retry_times=3 ,timeout_p=5):
    sigle = Urlsingle()
    agent_firefox = sigle._useragent_f
    cookie_firefox = sigle._cookie_f
    try:
        send_headers = {
            'User-Agent': agent_firefox,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
        }

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
            html_content = get_url_content(url, retry_times - 1)
        else:
            logging.warning('download fail(retry times >5)')

    return html_content



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

#获取成功返回1否则返回0
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



def mkdir(mkdir_path):
    path = mkdir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path

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

# print get_url_content("http://httpstat.us/500")
if __name__ == "__main__":
    global gstart_page
    global gstart_pos

    sigle = Urlsingle()
    #如果发生中断，手工设置下面的断点，不用担心下一页的起始位置，会默认设置为1
    init()
    atexit.register(save_2_file)
    continue_pos = gstart_pos
    if continue_pos != 0:
        print '----------------------warning-------------------'
        print 'startpos not zero '
    logging.basicConfig(filename='log\\a.log',level=logging.DEBUG)
    save_path = mkdir("savedir\\")
    for index in range(gstart_page, gstart_page+100):  # 按照ID来爬整个网站
        gstart_page = index
        src = sigle._scrapyurl % (index)
        print 'try to fetch: ', src
        logging.info('start trying to fetch page_num: '+str(index))
        url_content = get_url_content(src)
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
            son_save_path = mkdir(save_path + str(index) + "\\")
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

                son_content = get_url_content(son_url,5,3)
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