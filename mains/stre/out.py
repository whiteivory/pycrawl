#!/usr/bin/env python
# -*- coding: utf-8 -*-
#作用：将解压文件夹里的文件全都移动到上一层文件并根据imgs里面图片自动改名

import os

#for save status in case of error happens
def get_size(path):
	return os.path.getsize(path)

#move to parent directory
def get_file_to_pd(file_path):
	parent_path = os.path.dirname(os.path.dirname(os.path.realpath(file_path)))
	file_name = os.path.basename(file_path)

	file_path = os.path.realpath(file_path)
	rename_name = parent_path+os.sep+file_name
	print 'rename '+file_path+' to '+ rename_name
	os.rename(file_path, rename_name)

# traverse root directory, and list directories as dirs and files as files
def recruise(walk_root_path,dic={}):	
	for root, dirs, files in os.walk(walk_root_path):
		if os.path.basename(root) != 'imgs':
			path = root.split(os.sep)
			print((len(path) - 1) * '---', os.path.basename(root))
			for file in files:
				if file != os.path.basename(__file__):
					file_path = root+os.sep+file
					print(len(path) * '---', file, get_size(file_path))

					name_wt_ext = os.path.splitext(file)[0]
					name_ext = os.path.splitext(file)[1]
					if name_wt_ext in dic:
						v = dic[name_wt_ext]
					else:
						v = name_wt_ext
					new_name = v+name_ext
					new_file_path = root+os.sep+new_name
					
					#根据查字典找到新的名字
					os.rename(file_path,new_file_path)
					#复制到上一层
					get_file_to_pd(new_file_path)

def get_pic_code(name_str):
	if name_str != '':
		tmp = name_str.split("@")
		if len(tmp) <= 1 or len(tmp[0]) > 10:
			ret = ''
		else:
			ret =  tmp[0]
	else:
		ret = ''
	return ret

def get_dic(pics_path):
	dic ={}
	for root, dirs, files in os.walk(pics_path):
		for file in files:
			#print file
			k = get_pic_code(file)
			#print k
			if k: #返回空字符串则不记录当前文件
				v = os.path.splitext(file)[0]
				dic[k] = v
	return dic

dic = get_dic("imgs")
recruise(".",dic)