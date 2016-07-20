# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 15:31:13 2016
    #setUpDB
    #for x in range(postSection): 
    #    getPageList() --done
    #    parsePageList()
    #    cleanText()
    #    commitToDB()
@author: KimballWu
"""

import xml.etree.ElementTree as etree
import pandas as pd
import os,sys
import sqlite3
import mwparserfromhell as mwparser

sys.path.append('d:/coding/pythonlib')
import reUtil
os.chdir('d:/coding/textmine/')
wiki='corpus/zhwiki-20160701-pages-articles-multistream.xml'
wikiVer=wiki.replace('.xml','').split('/')[-1]
nameSpace='http://www.mediawiki.org/xml/export-0.10/'
#%%


#%%

def fullTag(tag,nameSpace=nameSpace,prefix=None):
    result='{{{}}}{}'.format(nameSpace,tag)
    if prefix!=None:
        return prefix+result
    else:
        return result


def parseMain(pageList):
        parse(pageList)

#%%


#main

##create db
con=sqlite3.connect('corpus/'+wikiVer)
cur=con.cursor()
try:
    cur.execute('Drop TABLE wiki')
except:
    cur.execute('''CREATE TABLE wiki(id BIGINT, timestamp DATETIME, title NVARCHAR, text NVARCHAR)''')
#%%

## go parse
count=0
commitCount=0
pageList=[]
for event, obj in etree.iterparse(xml, events=['end']):
    if obj.tag==fullTag('page'):
    count+=1
    pageList.append(obj)
    if count==200: # submit every 200 entry
        parseMain(pageList)
        commitToDB(data)
        commitCount+=1
        print '{} commit sucess!'.format(commitCount)
        count=0
        pageList=[]
#last time
parseMain(pageList)
commitToDB(data)
#%%



def getPageList(xml,start,end):
    pageList=[]
    count=0
    for event, obj in etree.iterparse(xml, events=['end']):
        if obj.tag==fullTag('page'):
            count+=1
            if count<start:
                continue
            elif count>=start and count<=end:
                pageList.append(obj)
            else:
                break
    return pageList

a=getPageList(wiki,10,20)



#parse page List to dataFrame
pageList=a
pageList=[x for x in pageList if x.find(fullTag('ns',prefix='./')).text=='0']
tagList=['id','timestamp','title','text'] 
result=[]
for tag in tagList:
    result.append([x.find(fullTag(tag,prefix='.//')).text for x in pageList])
data=pd.DataFrame(result).T    
data.columns=tagList
