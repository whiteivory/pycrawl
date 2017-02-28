#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

outfile = 'dic.txt'
fileHandle = open ( outfile, 'w' ) 

def recruise(walk_root_path,sep,ignorefiles):	
	code = 100000
	for root, dirs, files in os.walk(walk_root_path):
		for file in files:
			if file != os.path.basename(__file__) and file not in ignorefiles:
				file_path = root+os.sep+file

				name_wt_ext = os.path.splitext(file)[0] #name without extention
				name_ext = os.path.splitext(file)[1] #extention 

				fileHandle.write(str(code)+sep+file+"\n")
				new_name = str(code)+name_ext
				code = code+1
				new_file_path = root+os.sep+new_name
				print file_path
				print new_file_path
				os.rename(file_path,new_file_path)

igfiles = ['dc.py','rn.py',outfile,'save.txt','list.txt','list2.txt']
recruise(".",'@@',igfiles)
fileHandle.close()
shutil.copy(outfile,'save.txt')