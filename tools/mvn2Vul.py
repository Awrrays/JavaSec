#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2022-11-24 14:29:40
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import httpx
import re
import sys
import time
from bs4 import BeautifulSoup

from rich.progress import track
from rich.console import Console


banner = '''
                           _____  _   _       _ 
                          / __  \| | | |     | |
     _ __ _____   ___ __  `' / /'| | | |_   _| |
    | '_ ` _ \ \ / / '_ \   / /  | | | | | | | |
    | | | | | \ V /| | | |./ /___\ \_/ / |_| | |
    |_| |_| |_|\_/ |_| |_|\_____/ \___/ \__,_|_|
                                      仙友道@王半仙                                                    
'''

console = Console()
console.print(banner)

soup = BeautifulSoup(open(sys.argv[1], mode='r', encoding='utf-8'), 'lxml')
dependencys = soup.select("dependency")

headers = {
    'User-Agent':'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11'
}

# noneVersionPat = '<span data-snyk-test="VulnerableVersions: version.*>([\s\S]*?)</span>'
noneVulPat = '<a href="vuln.*>([\s\S]*?)<'

allDependencys = []
result = {}

console.print('[white][+] Parsing pom.xml...')

for i in dependencys:
    groupid = i.select('dependency > groupid')[0].string
    artifactId = i.select('dependency > artifactId')[0].string
    if len(i.select('dependency > version')) != 0:
        version = i.select('dependency > version')[0].string
    else:
        version = ''

    allDependencys.append([groupid, artifactId, version])
    console.print('  [yellow]' + groupid + '[white]/[green]' + artifactId + '[white]:' + version)


for step in track(range(len(allDependencys)), description="[+] Checking vulnerabilities for pom.xml"):

    url = 'https://security.snyk.io/package/maven/' + allDependencys[step][0] + '%3A' + allDependencys[step][1] + '/' + allDependencys[step][2]

    try:
        response = httpx.get(url, headers=headers, timeout=3)
    except:
        print('[!] Connect Timeout => ' + allDependencys[step][1])
        continue
    
    vul = re.findall(noneVulPat, response.text)

    if len(vul) == 0:
        continue

    result[allDependencys[step][0] + '/' + allDependencys[step][1] + '/' + allDependencys[step][2]] = []

    for i in vul:
        result[allDependencys[step][0] + '/' + allDependencys[step][1] + '/' + allDependencys[step][2]].append(i.strip())
        

for i in result.keys():
    console.print('[green]  ' + i + '[white] => [blue underline]https://mvnrepository.com/artifact/' + i)
    console.print('[red]    [Vulnerability]: ' + str(set(result[i])).replace('{', '').replace('}', '').replace("'", '')[:80])


