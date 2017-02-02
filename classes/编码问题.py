#!/usr/bin/env python
# -*- coding: utf-8 -*-

#首先理解decode和encode是分别将str字节流转换成unicode python对象和反之
#unicode对象并不是字节流，一般起不同字节流之间中介的作用

#首先coding:utf-8是必要的，这是python parser能够解析一个含有utf-8字符文件的基础
#因为parser不够智能检测出其编码

#然后关于字符串前的u表示什么
str = u'你好'
print type(str)#unicode对象
print str.encode('mbcs') #windows cmd用gbk、mbcs对字节流解码
#表示和如下相同
str ='你好'
print type(str)#str
print type(str.decode('utf-8')) #unicode
print str.decode('utf-8').encode('mbcs')
#所以u相当于decode的作用

str = '你好'
str.decode('utf-8')
print type(str) #str 说明并不对本身改变
str1 = str.decode('utf-8')
print type(str) #unicode 返回unicode
str2 = str1.encode('mbcs')
print type(str) #str 所谓str就是一个字节序，所以encode就是又变成了一个字节序
#这点从chardet上也能看出来chardet.detect(str1)会出错，因为它要求一个字节序，str2就可以

print '---------'
str1= 'asdfew'

str2 = '你好'
print type(str1+str2.decode('utf-8'))#unicode 另外注意str2如上所说本身没有变化
#两个相加，如果是两个字节流，那么直接相加变成字节流str
#但如果是一个字节流一个unicode，那么字节流默认会调用decode('ascii')转换成unicode
#这里str1还好，如果str2+str2.decode('utf-8')那么就会出错，因为ascii不能decode中文，超过了128的限制
#所以不要让隐式转换发生，自己应该显示调用
print type(u'str'+str2.decode('utf-8'))#unicode
print type(u'str'.encode('gbk')+str2) #两个str相加为str
print type(u'str'.encode('gbk')) #str
print type(u'str'.encode('gbk')+str2.decode('utf-8'))#str与unicode相加变unicode

#再说下print的问题，cmd采用gbk解码字节流，所以print应该是一个已经编码成gbk、mbcs的字节流
#如果你不这么做，直接print str2，有两种情况发生，
#第一种gbk能够按照自己的规则解码这个字节流，但显然解码出来为乱码
print str2 #浣犲ソ
#第二种，gbk规则解码不了，抛出错误或者异常

#关于文件内容和文件名
#文件内容比较智能，能够自动检测其中的字节流为什么样的编码（对于大部分editor是这样的
#但是windows写字板就不行，记事本可以)所以写入时候不用decode
#然而文件名就没那么智能，只能用gbk去识别文件名的字节流
#然而open函数这里性质不一样，open函数有两种重载，一是接受一个字节流，它会用一个默认的编码去decode，
#然后encode成gbk字节流供操作系统识别，或者原封不动把原编码字节流写进去，windows直接用gbk解码显示，
#和cmd不同的是，windows文件系统如果解码不出来某个字符不会像cmd抛出异常而是用默认字符显示
#二是传入一个unicode对象，那么就直接对这个unicode对象encode成gbk就可以了，显然这一种方法不容易乱码
#f=open(save_pic_name.decode('utf-8'),'wb')#必须是二进制形式，否则会图片乱码
#print >>f,html_content

#我猜cmd没有韩文，字体所以韩文都是问号默认显示，但显然gbk已经正常解码所以没有出错，而且写入文件都可以正常显示所以不影响

#两个重要的关系：
#1、ascii向后兼容各种编码，也就是ascii字节流用任何编码方式都可以正常解码
#str = 'abc' 这是ascii编码，但仍然可以用str.decode('gbk')不出错
#2、两个不同字节流之间不要相加，除了ascii可以和其他编码相加，原因上一条
str1 = u'你好'.encode('gbk')
str2 = u'와이스'.encode('utf-8')
print (str1+str2).decode('gbk').encode('gbk')
#这样会出错是因为gbk和utf-8两个不兼容的字节流相互相加，相加本身不会出错，但无论用utf-8
#还是gbk都不能解码这个字节流，也就是说这个字节流根本没有办法解析，除非你知道从哪个字节开始
#换了另一个编码
#ascii可以和其他编码相加，原因上一条
str1 = u'nihao'.encode('ascii')
str2 = u'你好'.encode('utf-8')#utf-8改成gbk同样可以运行
(str1+str2).decode('utf-8').encode('utf-8')#

#另外的一些编码问题可以在fancam.py里面搜索 编码问题 来看具体解决方式

#现在唯一没有办法解决的问题就是读取文件名或者目录名的问题
#有两个使用情景
#1、根据文件名生成html，因为我为了方便把大量信息都放在文件名里面了
#2、生成当前文件树结构
#这两个都无一例外要用到Python函数库里面读取文件名的函数，
# 自己无法控制要求用什么样的编码去读，从而自带函数默认对于无法解码的显示成？
# 目前我发现中文没问题，但是韩文就会显示成？，不知道是什么奇怪的编码导致的
# 两种对应解决方式：
# 1、所以以后信息不要存储在文件名里，因为你不知道系统的一些函数的解码方式
# 2、用cmd里的tree /f 命令，由于cmd>list.txt 重定向也会有问号问题，所以输出到控制台用复制的方式
# 如果很多看看有没有分页显示的命令。
#也都无一例外的
#补充一个：re.sub("[.:?]","@",text)这种用法时最好传入utf-8或者unicode，一般都可以正常工作
#还有不要乱替换字符，替换成&的话encode成GB2312会出问题（应该是&直接参与了编码），mbcs倒是没问题