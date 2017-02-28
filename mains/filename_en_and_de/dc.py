#!/usr/bin/env python
# -*- coding: utf-8 -*-
#decode
import os
import chardet
import re

def makedic(dic={},sep='@@'):
	infile = 'dic.txt'
	fileHandle = open ( infile, 'r' ) 
	done = 0
	while not done:
		line = fileHandle.readline()
		if line == '':
			done = 1
			break
		arr = line.split(sep)
		dic[arr[0]] = re.sub('\n','',arr[1])
	fileHandle.close()

def recruise(walk_root_path,dic,ignorefiles=[]):	
	for root, dirs, files in os.walk(walk_root_path):
		for file in files:
			if file != os.path.basename(__file__) and file not in ignorefiles:
				file_path = root+os.sep+file

				name_wt_ext = os.path.splitext(file)[0] #name without extention
				name_ext = os.path.splitext(file)[1] #extention 

				if name_wt_ext in dic:
					new_name = dic[name_wt_ext]
				else:
					new_name = name_wt_ext

				new_file_path = root+os.sep+new_name+name_ext
				
				#print file_path
				#print new_file_path
				os.rename(file_path,new_file_path)

igfiles=['dic.txt','rn.py','dc.py','save.txt','list.txt','list2.txt']
dic = {}
makedic(dic,'@@')
recruise('.',dic,igfiles)