import re
import json
import sys
import os
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


def getClass(variable, content):
	return list(set(re.findall('([\w<>, ]*?) ' + variable + '.[;=]', content)))

def getVariable(method, content):
	return list(set(re.findall('\W(\w*?)\.' + method, content)))

def methodToMethod(method, content):
	return list(set(re.findall('([\.\s]\w*?\(.*?\)\s*?\.' + method + ')', content)))
	# return list(set(re.findall('(\.\w*?\(.*?\)\.' + method + ')', content)))

def getMethod(content):
	return list(set(re.findall('\.(\w*?)\(', content)))


def check_regexp(keywords, content):

	vulList = {
		'ClassInvokeMethod':[],
		'MethodInvokeMethod':[]
	}

	for method in getMethod(content):
		for classification in keywords.keys():
			for i in keywords[classification]:
				if method == i['Method']:
					for variable in getVariable(method, content):
						
						if variable != '':
							clazzs = getClass(variable, content)
							if clazzs == []:
								if variable == i['Class']:
									vulDict = {
										'VulClassification':classification,
										'Alias':i['Alias'],
										'Sink':variable + '.' + method
									}
									if vulDict not in vulList['ClassInvokeMethod']:
										vulList['ClassInvokeMethod'].append(vulDict)
							else:
								for clazz in clazzs:
									if clazz.strip() == i['Class']:
										vulDict = {
											'VulClassification':classification,
											'Alias':i['Alias'],
											'Sink':variable + '.' + method
										}
										if vulDict not in vulList['ClassInvokeMethod']:
											vulList['ClassInvokeMethod'].append(vulDict)
						else:
							for method2Method in methodToMethod(method, content):
								vulList['MethodInvokeMethod'].append(method2Method)

	return vulList


def vulEcho(vulList, contentLine):
	for i in result['ClassInvokeMethod']:
		for line in range(len(contentLine)):
			if i['Sink'] in contentLine[line]:
				console.print('\tLine: ' + str(line + 1) + ' found ' + i['Alias'] + ' ' + i['VulClassification'] + ' => ' + i['Sink'])

	for i in list(set(result['MethodInvokeMethod'])):
		for line in range(len(contentLine)):
			if '\n' in i:
				if ' .' + i.rsplit('.', 1)[1] in contentLine[line]:
					console.print('\tLine: ' + str(line + 1) + ' Maybe has issue => ' + i.replace('\n', '').replace(' ', ''))
			else:
				if i in contentLine[line]:
					console.print('\tLine: ' + str(line + 1) + ' Maybe has issue => ' + i)


def handlePath(path):
	dirs = os.listdir(path) 

	path_suffix = ['.java', '.jsp', 'xml']

	for d in dirs:
		subpath = os.path.join(path, d) 
		if os.path.isfile(subpath):
			if os.path.splitext(subpath)[1] in path_suffix:
				allFiles.append(subpath)
		else:
			handlePath(subpath) 


if __name__ == '__main__':

	console = Console()
	console.print(banner)

	tPath = sys.argv[1]

	console.print("[*] Find vul keyword from " + tPath)

	allFiles = []
	handlePath(tPath)


	f = open('newKeywords.json', 'r')
	keywords = json.loads(f.read())
	f.close()

	for filename in allFiles:

		if not filename.endswith('xml'):

			fileRead = open(filename, 'r')
			content = fileRead.read()
			contentLine = content.split('\n')
			fileRead.close()

			if filename.endswith('.java'):
				noneComment = remove_comment(content)
			else:
				noneComment = content

			if not noneComment:
				continue
			
			result = check_regexp(keywords, noneComment)

			if result['ClassInvokeMethod'] == [] and result['MethodInvokeMethod'] == []:
				continue

			# print(result['MethodInvokeMethod'])

			console.print("[green][+] KeyWord in File: " + filename.replace(tPath, ''))

			vulEcho(result, contentLine)
		

	

	

	
	

							










