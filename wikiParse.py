# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 15:31:13 2016
    #setUpDB
    #for x in range(postSection):
    #    getPageList()
    #    parsePageList()
    #    cleanText()
    #    commitToDB()
@author: KimballWu
"""

import xml.etree.ElementTree as etree
import pandas as pd

xml='textmine/corpus/zhwiki-20160701-pages-articles-multistream.xml'
nameSpace='http://www.mediawiki.org/xml/export-0.10/'
#%%

def fullTag(tag,nameSpace=nameSpace,prefix=None):
    result='{{{}}}{}'.format(nameSpace,tag)
    if prefix!=None:
        return prefix+result
    else:
        return result

def getPageList(start,end):
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


#%%

# parse page List to dataFrame
#pageList=a
#pageList=[x for x in pageList if x.find(fullTag('ns',prefix='./')).text=='0']
#tagList=['id','timestamp','title','text'] 
#result=[]
#for tag in tagList:
#    result.append([x.find(fullTag(tag,prefix='.//')).text for x in pageList])
#data=pd.DataFrame(result).T    
#data.columns=tagList


        