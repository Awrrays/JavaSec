#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2022-11-27 11:54:00
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import re
import os
import json
import sys

from lxml.html import etree
from rich.console import Console


banner = '''
	 _             ___  ___      _       _     
	| |            |  \/  |     | |     | |    
	| | _____ _   _| .  . | __ _| |_ ___| |__  
	| |/ / _ \ | | | |\/| |/ _` | __/ __| '_ \ 
	|   <  __/ |_| | |  | | (_| | || (__| | | |
	|_|\_\___|\__, \_|  |_/\__,_|\__\___|_| |_|
	           __/ |                           
	          |___/                仙友道@王半仙            
'''

def remove_comment(content):

	singlelinePat = '//.*?\n'
	multilinePat = '/\*[\s\S]*?\*/'

	content = re.sub(singlelinePat, '', content)
	content = re.sub(multilinePat, '', content)

	return content

def check_regexp(keywords, filename):

	result = []

	lines = []

	file = open(filename, 'r')

	content = file.read()
	fileList = content.split('\n')
	if filename.endswith('.java'):
		noneComment = remove_comment(content)
	else:
		noneComment = content

	if not noneComment:
		return result

	for i in keywords.keys():
		# if i != 'ComponentsVul':
		# 	continue
		for j in keywords[i].keys():
			# if j != 'FastJson-2' and j != 'FastJson':
			# 	continue

			if '&' in keywords[i][j]:
				pats = keywords[i][j].split('&')
				# print(pats)
				# print(re.findall(pats[1], noneComment, re.I))

				if re.search(pats[0], noneComment, re.I) and re.search(pats[1], noneComment, re.I):
					datas = re.findall(pats[1], noneComment, re.I)
					for data in set(datas):
						for line in range(len(fileList)):
							if str(data) in fileList[line]:
								if str(line + 1) not in lines:
									lines.append(str(line + 1))
									result.append((i, j + ' => ' + keywords[i][j].split('&')[1].replace('\\', ''), str(line + 1)))
			else:
				datas = re.findall(keywords[i][j], noneComment, re.I)
				for data in set(datas):
					for line in range(len(fileList)):
						if str(data) in fileList[line]:
							if str(line + 1) not in lines:
								lines.append(str(line + 1))
								result.append((i, j, str(line + 1)))

	file.close()
	return result



def handlePath(path):
	dirs = os.listdir(path) 

	for d in dirs:
		subpath = os.path.join(path, d) 
		if os.path.isfile(subpath):
			if os.path.splitext(subpath)[1] == '.java' or os.path.splitext(subpath)[1] == '.xml':
				allFiles.append(subpath)
		else:
			handlePath(subpath) 



if __name__ == '__main__':

	console = Console()
	console.print(banner)

	tPath = sys.argv[1]
	console.print("[*] Find vul keyword from " + tPath)

	allFiles = []

	f = open('keywords.json', 'r')
	keywords = json.loads(f.read())
	f.close()

	handlePath(tPath)

	for i in allFiles:
		
		iVul = check_regexp(keywords, i)
		if len(iVul) != 0:
			console.print("[green][+] KeyWord in File: " + i.replace(tPath, ''))
			for j in iVul:
				console.print('\tLine: ' + j[2] + ' => ' + j[0] + ' - ' + j[1])
	

	# check_regexp(keywords, "/Users/awrrays/Desktop/JavaSec/jshERP-3.1/jshERP-boot/src/main/java/com/jsh/erp/utils/StringUtil.java")


