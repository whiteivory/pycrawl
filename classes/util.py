#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

#单利
class Util:
	__instance=None
	def __new__(cls,*args,**kwd):
		if Util.__instance is None:
			Util.__instance=object.__new__(cls,*args,**kwd)
		return Util.__instance

	def mkdir(self,mkdir_path):
		path = mkdir_path.strip()
		if not os.path.exists(path):
			os.makedirs(path)
		return path