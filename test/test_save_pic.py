#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.pycrawl import Pycrwal

pc = Pycrwal();
header ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
pc.save_pic_urllib('','http://pic.qiushibaike.com/system/pictures/11847/118470838/medium/app118470838.jpg','a','jpg',header)
#print html
