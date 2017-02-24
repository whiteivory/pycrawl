#!/usr/bin/env python
# -*- coding: utf-8 -*-

#要将&amp; 全部替换成&
import re
from urllib import unquote
def get_links(str):
	reg = 'href="(.*?)"'
	patten = re.compile(reg,re.S)
	return patten.findall(str)

file_o = open ("a.txt","r")
content = file_o.read()
ret = get_links(content)
f = open("links.txt","w")
for i in range(len(ret)):
	f.writelines(unquote(ret[i])+'\n')

	

# dir=os.curdir
# outfile="t.txt"
# file = open(outfile,"w")
# if not file:
# print ("cannot open the file %s for writing" % outfile)
# ListFilesToTxt(dir,file,wildcard, 1)
